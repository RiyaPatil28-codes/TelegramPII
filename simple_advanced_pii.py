#!/usr/bin/env python3
"""
Advanced PII Detector with Sentence-BERT Embeddings and Enhanced Clustering
Uses Sentence-BERT, TF-IDF, DBSCAN, K-Means, and NER for comprehensive PII detection
"""

import re
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    nlp = None

logger = logging.getLogger(__name__)

class SimplifiedAdvancedPIIDetector:
    def __init__(self):
        """Initialize advanced PII detector with Sentence-BERT and enhanced clustering"""
        self.setup_patterns()
        self.setup_pii_keywords()
        self.setup_vectorizer()
        self.setup_sentence_transformer()
        self.setup_ner_model()
        self.pii_embeddings_cache = {}
        self.normal_text_embeddings = None
        self._initialize_normal_embeddings()
        
    def setup_patterns(self):
        """Setup regex patterns for PII detection"""
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+91[\-\s]?|0?91[\-\s]?)?[789]\d{9}',
            'aadhar': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'passport': r'\b[A-Z]{1}[0-9]{7}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'pan': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            # New patterns for enhanced PII detection
            'birth_date': r'\b(?:0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](?:19|20)\d{2}\b|\b(?:19|20)\d{2}[\/\-\.](0?[1-9]|1[012])[\/\-\.](0?[1-9]|[12][0-9]|3[01])\b',
            'id_number': r'\b(?:ID|id|Id)[\s\-\#\:]*[A-Z0-9]{6,15}\b',
            'driver_license': r'\b[A-Z]{1,2}\d{6,8}\b|\bDL[\s\-\#]*[A-Z0-9]{8,15}\b',
            'place_name': r'\b(?:live in|from|at|in|near|visiting|traveled to|going to|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:city|town|village|state|country|district|county|province))?)\b'
        }
        
        # Common place name patterns
        self.place_indicators = [
            r'\b(?:Mumbai|Delhi|Bangalore|Chennai|Kolkata|Hyderabad|Ahmedabad|Pune|Surat|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Thane|Bhopal|Visakhapatnam|Patna|Vadodara|Ghaziabad)\b',
            r'\b(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|Charlotte|San Francisco|Indianapolis|Seattle|Denver|Washington|Boston)\b',
            r'\b(?:London|Birmingham|Manchester|Glasgow|Sheffield|Liverpool|Edinburgh|Bristol|Cardiff|Leicester|Coventry|Belfast|Nottingham|Newcastle|Brighton|Hull|Plymouth|Stoke|Wolverhampton|Derby)\b',
            r'\b(?:California|Texas|Florida|New York|Pennsylvania|Illinois|Ohio|Georgia|North Carolina|Michigan|New Jersey|Virginia|Washington|Arizona|Massachusetts|Tennessee|Indiana|Missouri|Maryland|Wisconsin)\b',
            r'\b(?:Maharashtra|Karnataka|Tamil Nadu|Andhra Pradesh|Kerala|West Bengal|Gujarat|Rajasthan|Madhya Pradesh|Uttar Pradesh|Haryana|Punjab|Bihar|Odisha|Assam|Jharkhand|Chhattisgarh|Himachal Pradesh|Uttarakhand|Tripura)\b'
        ]
        
    def setup_pii_keywords(self):
        """Setup contextual keywords for PII detection"""
        self.pii_keywords = {
            'personal_info': [
                'name', 'full name', 'first name', 'last name', 'surname', 'family name',
                'address', 'home address', 'street address', 'residential address',
                'date of birth', 'dob', 'birth date', 'birthday', 'born on', 'age',
                'my name is', 'i am', 'called me', 'they call me'
            ],
            'contact_info': [
                'phone', 'mobile', 'cell', 'telephone', 'number', 'contact',
                'call me', 'reach me', 'phone number', 'mobile number',
                'email', 'e-mail', 'mail', 'email address', 'contact email'
            ],
            'financial': [
                'account', 'bank account', 'account number', 'routing number',
                'credit card', 'debit card', 'card number', 'cvv', 'cvv2',
                'salary', 'income', 'earnings', 'payment', 'bank details'
            ],
            'identification': [
                'aadhar', 'aadhaar', 'passport', 'passport number',
                'license', 'driving license', 'dl number', 'driver license',
                'pan', 'pan card', 'voter id', 'voter card', 'ssn', 'social security',
                'id number', 'identification', 'identity card', 'government id'
            ],
            'location': [
                'live in', 'live at', 'from', 'based in', 'located in', 'residing in',
                'address is', 'home is', 'staying at', 'visiting', 'traveled to',
                'going to', 'city', 'town', 'state', 'country', 'zip code', 'pincode'
            ]
        }
        
    def setup_vectorizer(self):
        """Setup TF-IDF vectorizer"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            lowercase=True
        )
        
    def setup_sentence_transformer(self):
        """Setup Sentence-BERT model for semantic embeddings"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use lightweight but effective model
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Sentence-BERT model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Sentence-BERT: {e}")
                self.sentence_model = None
        else:
            logger.warning("Sentence-Transformers not available, using TF-IDF only")
            self.sentence_model = None
    
    def setup_ner_model(self):
        """Setup spaCy NER model"""
        if SPACY_AVAILABLE and nlp:
            self.ner_model = nlp
            logger.info("spaCy NER model loaded successfully")
        else:
            logger.warning("spaCy not available, using pattern matching only")
            self.ner_model = None
    
    def _initialize_normal_embeddings(self):
        """Pre-compute embeddings for normal conversation patterns"""
        if self.sentence_model:
            normal_corpus = [
                "Hello how are you doing today",
                "The weather is nice and sunny",
                "I enjoy reading books and watching movies",
                "Thank you for your help and assistance",
                "Have a wonderful day ahead",
                "Nice to meet you and chat",
                "Looking forward to hearing from you",
                "Hope you are doing well",
                "What are your hobbies and interests",
                "How was your weekend",
                "Great to hear from you",
                "Let me know if you need anything"
            ]
            try:
                self.normal_text_embeddings = self.sentence_model.encode(normal_corpus)
                logger.info("Normal text embeddings computed")
            except Exception as e:
                logger.warning(f"Failed to compute normal embeddings: {e}")
                self.normal_text_embeddings = None
        
    def detect_pii_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using regex patterns with enhanced confidence"""
        detected = []
        
        # Standard pattern matching
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with groups, take the first group or join all
                    match = match[0] if match[0] else ' '.join(filter(None, match))
                
                # Enhanced confidence based on pattern complexity
                confidence = self.calculate_regex_confidence(pii_type, match)
                
                detected.append({
                    'type': pii_type,
                    'value': match.strip(),
                    'confidence': confidence,
                    'method': 'enhanced_regex',
                    'context': self.get_context(text, match)
                })
        
        # Additional place name detection using common place patterns
        for place_pattern in self.place_indicators:
            matches = re.findall(place_pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append({
                    'type': 'place_name',
                    'value': match.strip(),
                    'confidence': 0.85,
                    'method': 'place_pattern',
                    'context': self.get_context(text, match)
                })
        
        # Name detection using contextual patterns
        name_patterns = [
            r'\b(?:my name is|i am|i\'m|call me|they call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b(?:mr|mrs|ms|dr|prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:here|speaking|calling)\b'
        ]
        
        for name_pattern in name_patterns:
            matches = re.findall(name_pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append({
                    'type': 'person_name',
                    'value': match.strip(),
                    'confidence': 0.80,
                    'method': 'name_pattern',
                    'context': self.get_context(text, match)
                })
                
        return detected
    
    def calculate_regex_confidence(self, pii_type: str, value: str) -> float:
        """Calculate confidence based on PII type and value characteristics"""
        base_confidence = {
            'email': 0.95,
            'phone': 0.90,
            'aadhar': 0.92,
            'passport': 0.88,
            'credit_card': 0.85,
            'pan': 0.90,
            'ssn': 0.92,
            'ip_address': 0.75,
            'birth_date': 0.85,
            'id_number': 0.80,
            'driver_license': 0.85,
            'place_name': 0.75,
            'person_name': 0.70
        }
        
        confidence = base_confidence.get(pii_type, 0.70)
        
        # Adjust based on value characteristics
        if pii_type == 'email':
            if any(domain in value.lower() for domain in ['gmail', 'yahoo', 'outlook', 'hotmail']):
                confidence += 0.03
        elif pii_type == 'phone':
            if len(re.sub(r'[\s\-+()]', '', value)) == 10:
                confidence += 0.05
        elif pii_type == 'aadhar':
            if len(re.sub(r'[\s-]', '', value)) == 12:
                confidence += 0.03
        elif pii_type in ['person_name', 'place_name']:
            # Names and places need higher thresholds
            if len(value.split()) >= 2:
                confidence += 0.05
            if value[0].isupper():
                confidence += 0.05
        elif pii_type == 'birth_date':
            # Birth dates with separators are more confident
            if '/' in value or '-' in value or '.' in value:
                confidence += 0.05
        elif pii_type in ['id_number', 'driver_license']:
            # ID numbers with proper format
            if len(value) >= 8:
                confidence += 0.05
                
        return min(0.98, confidence)
    
    def detect_pii_contextual_advanced(self, text: str) -> List[Dict[str, Any]]:
        """Advanced contextual PII detection using keyword analysis"""
        detected = []
        text_lower = text.lower()
        words = text.split()
        
        for category, keywords in self.pii_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find words near the keyword that could be PII
                    keyword_positions = [i for i, word in enumerate(words) 
                                       if keyword.lower() in word.lower()]
                    
                    for pos in keyword_positions:
                        # Look at words around the keyword
                        window_start = max(0, pos - 3)
                        window_end = min(len(words), pos + 4)
                        window_words = words[window_start:window_end]
                        
                        for word in window_words:
                            if self.is_potential_pii_value(word, category):
                                detected.append({
                                    'type': f'contextual_{category}',
                                    'value': word,
                                    'confidence': 0.65,
                                    'method': 'contextual_advanced',
                                    'keyword': keyword,
                                    'context': ' '.join(window_words)
                                })
                                
        return detected
    
    def is_potential_pii_value(self, word: str, category: str) -> bool:
        """Check if a word is potentially PII based on category"""
        word_clean = re.sub(r'[^\w@.-]', '', word)
        
        if len(word_clean) < 3:
            return False
            
        # Category-specific checks
        if category == 'personal_info':
            return (word_clean.istitle() and 
                   len(word_clean) > 2 and 
                   word_clean.isalpha())
        elif category == 'contact_info':
            return ('@' in word_clean or 
                   re.match(r'\d+', word_clean))
        elif category == 'financial':
            return (word_clean.isdigit() and 
                   len(word_clean) >= 4)
        elif category == 'identification':
            return (len(word_clean) >= 6 and 
                   (word_clean.isdigit() or 
                    re.match(r'[A-Z0-9]+', word_clean.upper())))
                    
        return False
    
    def detect_pii_tfidf_clustering(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced TF-IDF with both DBSCAN and K-Means clustering"""
        try:
            detected = []
            
            # Expanded reference corpus of normal text
            normal_corpus = [
                "Hello how are you doing today",
                "The weather is nice and sunny",
                "I enjoy reading books and watching movies", 
                "Thank you for your help and assistance",
                "Have a wonderful day ahead",
                "Nice to meet you and chat",
                "Looking forward to hearing from you",
                "Hope you are doing well",
                "What are your hobbies and interests",
                "How was your weekend",
                "Great to hear from you",
                "Let me know if you need anything",
                "I hope this message finds you well",
                "Thanks for reaching out to me",
                "Have a great rest of your day"
            ]
            
            # Tokenize input text into sentences and phrases
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
            
            # Also extract phrases around potential PII indicators
            phrases = []
            for keyword_list in self.pii_keywords.values():
                for keyword in keyword_list:
                    if keyword.lower() in text.lower():
                        # Extract phrase around keyword
                        pattern = rf'.{{{0,20}}}{re.escape(keyword)}.{{{0,20}}}'
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        phrases.extend([m.strip() for m in matches if len(m.strip()) > 5])
            
            all_text_units = sentences + phrases
            if not all_text_units:
                return detected
                
            # Combine corpus with input text units
            all_texts = normal_corpus + list(set(all_text_units))  # Remove duplicates
            
            try:
                # Create TF-IDF matrix
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
                
                # Get vectors for input text units only
                input_vectors = tfidf_matrix[len(normal_corpus):]
                
                if input_vectors.shape[0] > 1:
                    input_array = input_vectors.toarray()
                    
                    # Apply DBSCAN clustering to find outliers
                    dbscan = DBSCAN(eps=0.4, min_samples=1, metric='cosine')
                    dbscan_labels = dbscan.fit_predict(input_array)
                    
                    # Apply K-Means clustering for alternative grouping
                    n_clusters = min(max(2, len(all_text_units) // 3), 5)
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    kmeans_labels = kmeans.fit_predict(input_array)
                    
                    # Analyze clustering results
                    for i, text_unit in enumerate(all_text_units):
                        dbscan_label = dbscan_labels[i]
                        kmeans_label = kmeans_labels[i]
                        
                        # Check if text unit has PII indicators
                        if self.sentence_has_pii_indicators(text_unit):
                            is_dbscan_outlier = (dbscan_label == -1)
                            kmeans_cluster_size = np.sum(kmeans_labels == kmeans_label)
                            
                            # Higher confidence for outliers and small clusters
                            base_confidence = 0.50
                            if is_dbscan_outlier:
                                base_confidence += 0.15
                            if kmeans_cluster_size <= 2:
                                base_confidence += 0.10
                            
                            # Extract PII terms from the text unit
                            pii_terms = self.extract_pii_terms_from_sentence(text_unit)
                            
                            for term in pii_terms:
                                term['confidence'] = min(0.95, term['confidence'] + base_confidence - 0.55)
                                term['clustering_info'] = {
                                    'dbscan_label': int(dbscan_label),
                                    'kmeans_label': int(kmeans_label),
                                    'is_outlier': is_dbscan_outlier,
                                    'cluster_size': int(kmeans_cluster_size)
                                }
                                detected.append(term)
                            
            except Exception as e:
                logger.warning(f"TF-IDF clustering processing error: {e}")
                
        except Exception as e:
            logger.warning(f"TF-IDF clustering error: {e}")
            
        return detected
    
    def sentence_has_pii_indicators(self, sentence: str) -> bool:
        """Check if sentence has PII indicators"""
        # Check for numeric sequences
        if re.search(r'\d{4,}', sentence):
            return True
            
        # Check for email patterns
        if '@' in sentence and '.' in sentence:
            return True
            
        # Check for multiple capitalized words (potential names)
        cap_words = re.findall(r'\b[A-Z][a-z]+\b', sentence)
        if len(cap_words) >= 2:
            return True
            
        # Check for PII keywords
        sentence_lower = sentence.lower()
        for keywords in self.pii_keywords.values():
            if any(keyword in sentence_lower for keyword in keywords):
                return True
                
        return False
    
    def extract_pii_terms_from_sentence(self, sentence: str) -> List[Dict[str, Any]]:
        """Enhanced extraction of potential PII terms from a sentence"""
        detected = []
        
        # Extract numeric sequences (potential IDs, phone numbers, etc.)
        numbers = re.findall(r'\b\d{4,}\b', sentence)
        for num in numbers:
            pii_type = 'numeric_sequence'
            confidence = 0.55
            
            # Classify based on length and context
            if len(num) == 12 and any(word in sentence.lower() for word in ['aadhar', 'aadhaar']):
                pii_type = 'aadhar'
                confidence = 0.85
            elif len(num) == 10 and any(word in sentence.lower() for word in ['phone', 'mobile', 'number']):
                pii_type = 'phone'
                confidence = 0.80
            elif len(num) == 9 and any(word in sentence.lower() for word in ['ssn', 'social']):
                pii_type = 'ssn'
                confidence = 0.85
            elif len(num) >= 6 and any(word in sentence.lower() for word in ['id', 'license', 'card']):
                pii_type = 'id_number'
                confidence = 0.70
                
            detected.append({
                'type': pii_type,
                'value': num,
                'confidence': confidence,
                'method': 'tfidf_clustering',
                'context': sentence.strip()
            })
            
        # Extract capitalized word sequences (potential names/places)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b', sentence)
        for noun in proper_nouns:
            words = noun.split()
            if len(words) >= 2:
                pii_type = 'potential_name'
                confidence = 0.60
                
                # Check if it's likely a place name
                if any(place_word in sentence.lower() for place_word in ['from', 'in', 'at', 'near', 'live', 'city', 'state']):
                    pii_type = 'place_name'
                    confidence = 0.75
                # Check if it's likely a person name
                elif any(name_word in sentence.lower() for name_word in ['name', 'i am', 'call me', 'mr', 'mrs', 'ms']):
                    pii_type = 'person_name'
                    confidence = 0.80
                    
                detected.append({
                    'type': pii_type,
                    'value': noun,
                    'confidence': confidence,
                    'method': 'tfidf_clustering',
                    'context': sentence.strip()
                })
        
        # Extract email patterns
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', sentence)
        for email in emails:
            detected.append({
                'type': 'email',
                'value': email,
                'confidence': 0.95,
                'method': 'tfidf_clustering',
                'context': sentence.strip()
            })
        
        # Extract date patterns that might be birth dates
        dates = re.findall(r'\b(?:0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](?:19|20)\d{2}\b', sentence)
        for date in dates:
            if any(word in sentence.lower() for word in ['birth', 'born', 'dob', 'birthday']):
                detected.append({
                    'type': 'birth_date',
                    'value': date,
                    'confidence': 0.90,
                    'method': 'tfidf_clustering',
                    'context': sentence.strip()
                })
            
        return detected
    
    def get_context(self, text: str, value: str) -> str:
        """Get context around a detected PII value"""
        pos = text.find(value)
        if pos == -1:
            return text[:50] + "..." if len(text) > 50 else text
            
        start = max(0, pos - 20)
        end = min(len(text), pos + len(value) + 20)
        return text[start:end].strip()
    
    def detect_pii_with_ner(self, text: str) -> List[Dict[str, Any]]:
        """Use NER to detect person names, organizations, and locations"""
        detected = []
        
        if not self.ner_model:
            return detected
            
        try:
            doc = self.ner_model(text)
            
            for ent in doc.ents:
                confidence = 0.75
                pii_type = 'unknown'
                
                if ent.label_ == "PERSON":
                    pii_type = 'person_name'
                    confidence = 0.85
                elif ent.label_ in ["GPE", "LOC"]:  # Geopolitical entity, Location
                    pii_type = 'place_name'
                    confidence = 0.80
                elif ent.label_ == "ORG":
                    pii_type = 'organization'
                    confidence = 0.70
                elif ent.label_ == "DATE":
                    # Check if it looks like a birth date
                    if any(word in text.lower() for word in ['birth', 'born', 'dob']):
                        pii_type = 'birth_date'
                        confidence = 0.90
                    else:
                        continue  # Skip regular dates
                else:
                    continue
                    
                detected.append({
                    'type': pii_type,
                    'value': ent.text,
                    'confidence': confidence,
                    'method': 'spacy_ner',
                    'context': self.get_context(text, ent.text),
                    'ner_label': ent.label_
                })
                
        except Exception as e:
            logger.warning(f"NER processing error: {e}")
            
        return detected
    
    def extract_sentence_embeddings(self, text: str) -> Optional[np.ndarray]:
        """Extract sentence embeddings using Sentence-BERT"""
        if not self.sentence_model:
            return None
            
        try:
            # Split into sentences for better embedding quality
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
            
            if not sentences:
                sentences = [text]
                
            embeddings = self.sentence_model.encode(sentences)
            
            # Average embeddings if multiple sentences
            if len(embeddings.shape) > 1 and embeddings.shape[0] > 1:
                return np.mean(embeddings, axis=0)
            else:
                return embeddings[0] if len(embeddings.shape) > 1 else embeddings
                
        except Exception as e:
            logger.warning(f"Embedding extraction error: {e}")
            return None
    
    def detect_pii_with_embeddings_clustering(self, text: str) -> List[Dict[str, Any]]:
        """Use Sentence-BERT embeddings with DBSCAN and K-Means clustering"""
        detected = []
        
        if not self.sentence_model or self.normal_text_embeddings is None:
            return detected
            
        try:
            # Extract embeddings for input text
            input_embedding = self.extract_sentence_embeddings(text)
            if input_embedding is None:
                return detected
                
            # Calculate similarity with normal text patterns
            similarities = cosine_similarity([input_embedding], self.normal_text_embeddings)[0]
            max_similarity = np.max(similarities)
            avg_similarity = np.mean(similarities)
            
            # If text is very dissimilar to normal patterns, analyze further
            if max_similarity < 0.3 or avg_similarity < 0.2:
                # Text is anomalous, check for PII patterns
                
                # Tokenize and tag potential PII candidates
                pii_candidates = self.extract_pii_candidates(text)
                
                if pii_candidates:
                    # Use clustering on candidate embeddings
                    candidate_embeddings = []
                    valid_candidates = []
                    
                    for candidate in pii_candidates:
                        candidate_emb = self.extract_sentence_embeddings(candidate['context'])
                        if candidate_emb is not None:
                            candidate_embeddings.append(candidate_emb)
                            valid_candidates.append(candidate)
                    
                    if len(candidate_embeddings) > 1:
                        candidate_embeddings = np.array(candidate_embeddings)
                        
                        # Apply DBSCAN clustering
                        dbscan = DBSCAN(eps=0.4, min_samples=1, metric='cosine')
                        cluster_labels = dbscan.fit_predict(candidate_embeddings)
                        
                        # Apply K-Means as alternative clustering
                        n_clusters = min(3, len(candidate_embeddings))
                        if n_clusters > 1:
                            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                            kmeans_labels = kmeans.fit_predict(candidate_embeddings)
                        else:
                            kmeans_labels = np.zeros(len(candidate_embeddings))
                        
                        # Analyze clustering results
                        for i, candidate in enumerate(valid_candidates):
                            # Higher confidence for outliers (potential PII)
                            is_outlier = (cluster_labels[i] == -1)  # DBSCAN outlier
                            cluster_size = np.sum(kmeans_labels == kmeans_labels[i])
                            
                            confidence = candidate['base_confidence']
                            if is_outlier:
                                confidence += 0.15
                            if cluster_size == 1:  # Unique pattern in K-Means
                                confidence += 0.10
                                
                            detected.append({
                                'type': candidate['type'],
                                'value': candidate['value'],
                                'confidence': min(0.98, confidence),
                                'method': 'embedding_clustering',
                                'context': candidate['context'],
                                'clustering_info': {
                                    'dbscan_label': int(cluster_labels[i]),
                                    'kmeans_label': int(kmeans_labels[i]),
                                    'is_outlier': is_outlier,
                                    'similarity_score': float(max_similarity)
                                }
                            })
                    
        except Exception as e:
            logger.warning(f"Embedding clustering error: {e}")
            
        return detected
    
    def extract_pii_candidates(self, text: str) -> List[Dict[str, Any]]:
        """Extract candidate PII tokens using regex and contextual analysis"""
        candidates = []
        
        # Extract potential tokens based on patterns
        tokens = text.split()
        
        for i, token in enumerate(tokens):
            # Get context window
            start_idx = max(0, i - 3)
            end_idx = min(len(tokens), i + 4)
            context_tokens = tokens[start_idx:end_idx]
            context = ' '.join(context_tokens)
            
            # Check various PII patterns
            if re.match(r'\b[A-Z][a-z]+\b', token) and len(token) > 2:
                # Potential name
                candidates.append({
                    'type': 'potential_name',
                    'value': token,
                    'context': context,
                    'base_confidence': 0.60
                })
            
            elif re.match(r'\d{4,}', token):
                # Numeric sequence
                candidates.append({
                    'type': 'numeric_sequence',
                    'value': token,
                    'context': context,
                    'base_confidence': 0.65
                })
            
            elif '@' in token:
                # Potential email
                candidates.append({
                    'type': 'potential_email',
                    'value': token,
                    'context': context,
                    'base_confidence': 0.90
                })
        
        return candidates
    
    def comprehensive_pii_detection(self, text: str) -> Dict[str, Any]:
        """Run comprehensive PII detection using all available methods"""
        all_detected = []
        
        # Method 1: Enhanced regex detection
        regex_results = self.detect_pii_regex(text)
        all_detected.extend(regex_results)
        
        # Method 2: Advanced contextual detection
        contextual_results = self.detect_pii_contextual_advanced(text)
        all_detected.extend(contextual_results)
        
        # Method 3: NER-based detection
        ner_results = self.detect_pii_with_ner(text)
        all_detected.extend(ner_results)
        
        # Method 4: Sentence-BERT embeddings with clustering
        embedding_results = self.detect_pii_with_embeddings_clustering(text)
        all_detected.extend(embedding_results)
        
        # Method 5: TF-IDF clustering analysis (fallback)
        tfidf_results = self.detect_pii_tfidf_clustering(text)
        all_detected.extend(tfidf_results)
        
        # Consolidate results
        consolidated_results = self.consolidate_detections(all_detected)
        
        # Calculate overall confidence
        overall_confidence = self.calculate_overall_confidence(consolidated_results)
        
        return {
            'text': text,
            'pii_detected': len(consolidated_results) > 0,
            'pii_items': consolidated_results,
            'detection_methods': self.get_methods_used(consolidated_results),
            'overall_confidence': overall_confidence,
            'redacted_text': self.redact_text(text, consolidated_results)
        }
    
    def consolidate_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate and deduplicate detections"""
        if not detections:
            return []
            
        consolidated = []
        seen_values = set()
        
        # Sort by confidence
        sorted_detections = sorted(detections, key=lambda x: x.get('confidence', 0), reverse=True)
        
        for detection in sorted_detections:
            value = detection['value'].lower().strip()
            
            if value in seen_values or len(value) < 3:
                continue
                
            # Skip common words
            if value in ['the', 'and', 'for', 'you', 'are', 'this', 'that', 'with']:
                continue
                
            seen_values.add(value)
            consolidated.append(detection)
            
        return consolidated
    
    def calculate_overall_confidence(self, detections: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        if not detections:
            return 0.0
            
        # Weight by method reliability
        method_weights = {
            'enhanced_regex': 1.0,
            'spacy_ner': 0.9,
            'embedding_clustering': 0.85,
            'contextual_advanced': 0.7,
            'tfidf_clustering': 0.6,
            'name_pattern': 0.8,
            'place_pattern': 0.8
        }
        
        weighted_scores = []
        for detection in detections:
            method = detection.get('method', 'unknown')
            confidence = detection.get('confidence', 0)
            weight = method_weights.get(method, 0.5)
            weighted_scores.append(confidence * weight)
            
        return min(0.95, np.mean(weighted_scores))
    
    def get_methods_used(self, detections: List[Dict[str, Any]]) -> List[str]:
        """Get list of detection methods used"""
        methods = set()
        for detection in detections:
            methods.add(detection.get('method', 'unknown'))
        return list(methods)
    
    def redact_text(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Redact PII from text"""
        redacted = text
        
        # Sort by value length (longest first) to avoid partial replacements
        sorted_detections = sorted(detections, key=lambda x: len(x['value']), reverse=True)
        
        for detection in sorted_detections:
            value = detection['value']
            pii_type = detection['type']
            placeholder = f"[{pii_type.upper()}_REDACTED]"
            redacted = redacted.replace(value, placeholder)
            
        return redacted

# Global instance for simplified advanced detection
simplified_detector = SimplifiedAdvancedPIIDetector()

def detect_pii_advanced_simple(text: str) -> Dict[str, Any]:
    """Main function for simplified advanced PII detection"""
    return simplified_detector.comprehensive_pii_detection(text)

if __name__ == "__main__":
    # Test the simplified advanced detector
    test_text = "Hi, I'm John Smith from Mumbai. Email me at john.smith@gmail.com or call 9876543210. My Aadhar is 1234-5678-9012."
    
    result = detect_pii_advanced_simple(test_text)
    
    print("Simplified Advanced PII Detection Results:")
    print(f"Text: {result['text']}")
    print(f"PII Detected: {result['pii_detected']}")
    print(f"Overall Confidence: {result['overall_confidence']:.2f}")
    print(f"Methods Used: {result['detection_methods']}")
    print(f"Redacted Text: {result['redacted_text']}")
    print("\nDetected PII Items:")
    for item in result['pii_items']:
        print(f"  - {item['type']}: {item['value']} (confidence: {item['confidence']:.2f}, method: {item['method']})")