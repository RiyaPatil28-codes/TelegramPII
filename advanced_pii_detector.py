#!/usr/bin/env python3
"""
Advanced PII Detector with BERT, spaCy, TF-IDF, and Unsupervised Learning
Complete implementation with fallback handling for missing dependencies
"""

import re
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings("ignore")

# Try importing advanced ML libraries with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedPIIDetector:
    def __init__(self):
        """Initialize advanced PII detector with BERT and unsupervised learning"""
        self.setup_models()
        self.setup_patterns()
        self.setup_pii_keywords()
        
    def setup_models(self):
        """Initialize BERT, spaCy, and sentence transformer models"""
        # Initialize Sentence-BERT model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✓ Loaded Sentence-BERT model (all-MiniLM-L6-v2)")
            except Exception as e:
                logger.warning(f"Failed to load Sentence-BERT: {e}")
                self.sentence_model = None
        else:
            logger.warning("Sentence-transformers not available")
            self.sentence_model = None
            
        # Initialize spaCy NER model
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load('en_core_web_sm')
                logger.info("✓ Loaded spaCy NER model (en_core_web_sm)")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")
                self.nlp = None
        else:
            logger.warning("spaCy not available")
            self.nlp = None
            
        # Initialize TF-IDF and clustering models
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 3),
                    min_df=1
                )
                self.dbscan_model = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
                self.kmeans_model = KMeans(n_clusters=3, random_state=42, n_init=10)
                logger.info("✓ Loaded scikit-learn models (TF-IDF, DBSCAN, K-Means)")
            except Exception as e:
                logger.warning(f"Failed to load scikit-learn models: {e}")
                self.tfidf_vectorizer = None
                self.dbscan_model = None
                self.kmeans_model = None
        else:
            logger.warning("scikit-learn not available")
            self.tfidf_vectorizer = None
            self.dbscan_model = None
            self.kmeans_model = None
            
        # Initialize NLTK for tokenization
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data if not present
                import nltk
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
                logger.info("✓ Loaded NLTK tokenization and stopwords")
            except Exception as e:
                logger.warning(f"Failed to setup NLTK: {e}")
                self.stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        else:
            logger.warning("NLTK not available")
            self.stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
    def setup_patterns(self):
        """Setup regex patterns for PII detection"""
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+91[\-\s]?|0?91[\-\s]?)?[789]\d{9}',
            'aadhar': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'passport': r'\b[A-Z]{1}[0-9]{7}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'pan': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
    def setup_pii_keywords(self):
        """Setup contextual keywords for PII detection"""
        self.pii_keywords = {
            'personal_info': [
                'name', 'full name', 'first name', 'last name', 'surname',
                'address', 'home address', 'street address', 'zip code', 'pincode',
                'date of birth', 'dob', 'birthday', 'age', 'birth date'
            ],
            'contact_info': [
                'phone', 'mobile', 'contact', 'call me', 'reach me',
                'email', 'e-mail', 'mail address', 'contact email'
            ],
            'financial': [
                'account number', 'bank account', 'credit card', 'debit card',
                'card number', 'cvv', 'pin', 'salary', 'income'
            ],
            'identification': [
                'aadhar', 'aadhaar', 'passport', 'driving license', 'dl',
                'pan', 'pan card', 'voter id', 'social security', 'ssn'
            ],
            'location': [
                'live in', 'stay in', 'residing', 'located at', 'city',
                'state', 'country', 'locality', 'area', 'neighborhood'
            ]
        }
        
    def detect_pii_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using regex patterns"""
        detected = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                detected.append({
                    'type': pii_type,
                    'value': match.strip(),
                    'confidence': 0.95,
                    'method': 'regex',
                    'start_pos': text.find(match),
                    'end_pos': text.find(match) + len(match)
                })
                
        return detected
    
    def detect_pii_spacy_ner(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using spaCy Named Entity Recognition"""
        if not self.nlp:
            return []
            
        try:
            detected = []
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # Map spaCy entity types to PII types
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY', 'CARDINAL', 'TIME']:
                    confidence = 0.7
                    pii_type = ent.label_.lower()
                    
                    # Adjust confidence based on entity type
                    if ent.label_ == 'PERSON':
                        confidence = 0.85
                        pii_type = 'name'
                    elif ent.label_ == 'GPE':  # Geopolitical entity (locations)
                        confidence = 0.75
                        pii_type = 'location'
                    elif ent.label_ == 'DATE':
                        confidence = 0.6
                        pii_type = 'date'
                    elif ent.label_ == 'MONEY':
                        confidence = 0.8
                        pii_type = 'financial'
                    
                    detected.append({
                        'type': pii_type,
                        'value': ent.text,
                        'confidence': confidence,
                        'method': 'spacy_ner',
                        'spacy_label': ent.label_,
                        'start_pos': ent.start_char,
                        'end_pos': ent.end_char
                    })
                    
            return detected
            
        except Exception as e:
            logger.warning(f"spaCy NER error: {e}")
            return []
    
    def detect_pii_bert_clustering(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using BERT embeddings and unsupervised clustering"""
        if not self.sentence_model or not SKLEARN_AVAILABLE:
            return []
            
        try:
            detected = []
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            if len(sentences) < 2:
                return detected
                
            # Generate BERT embeddings for sentences
            embeddings = self.sentence_model.encode(sentences)
            
            # Use DBSCAN for clustering potentially sensitive sentences
            clusters = self.dbscan_model.fit_predict(embeddings)
            
            # Analyze clusters for PII patterns
            for i, cluster_id in enumerate(clusters):
                if cluster_id != -1:  # Not noise
                    sentence = sentences[i]
                    
                    # Check if sentence contains PII indicators
                    pii_indicators = self._analyze_sentence_for_pii(sentence)
                    
                    if pii_indicators:
                        detected.extend(pii_indicators)
                        
            return detected
            
        except Exception as e:
            logger.warning(f"BERT clustering error: {e}")
            return []
    
    def _analyze_sentence_for_pii(self, sentence: str) -> List[Dict[str, Any]]:
        """Analyze sentence for PII using linguistic patterns"""
        detected = []
        
        # Named entity patterns (capitalized words that might be names)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, sentence)
        
        for name in names:
            # Filter out common non-names
            common_non_names = ['Hello There', 'Thank You', 'Good Morning', 'Best Regards']
            if name not in common_non_names and len(name.split()) >= 2:
                detected.append({
                    'type': 'name',
                    'value': name,
                    'confidence': 0.7,
                    'method': 'bert_ner',
                    'context': sentence
                })
                
        # Location patterns
        location_indicators = ['in', 'at', 'from', 'live', 'stay', 'visit']
        for indicator in location_indicators:
            if indicator in sentence.lower():
                # Look for capitalized words after location indicators
                pattern = rf'\b{indicator}\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b'
                locations = re.findall(pattern, sentence, re.IGNORECASE)
                
                for location in locations:
                    detected.append({
                        'type': 'location',
                        'value': location,
                        'confidence': 0.6,
                        'method': 'bert_location',
                        'context': sentence
                    })
                    
        return detected
    
    def detect_pii_tfidf_clustering(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using TF-IDF vectorization and clustering"""
        if not self.tfidf_vectorizer or not SKLEARN_AVAILABLE:
            return []
            
        try:
            detected = []
            
            # Split text into sentences
            if NLTK_AVAILABLE:
                try:
                    sentences = sent_tokenize(text)
                except:
                    sentences = text.split('. ')
            else:
                sentences = text.split('. ')
                
            if len(sentences) < 2:
                return detected
                
            # Create PII keyword corpus for comparison
            pii_keyword_list = []
            for category, keywords in self.pii_keywords.items():
                pii_keyword_list.extend(keywords)
                
            # Combine sentences with PII keywords for vectorization
            all_texts = sentences + pii_keyword_list
            
            # Create TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate similarity between sentences and PII keywords
            sentence_vectors = tfidf_matrix[:len(sentences)]
            keyword_vectors = tfidf_matrix[len(sentences):]
            
            similarities = cosine_similarity(sentence_vectors, keyword_vectors)
            
            # Find sentences with high similarity to PII keywords
            for i, sentence in enumerate(sentences):
                max_similarity = np.max(similarities[i])
                
                if max_similarity > 0.3:  # Threshold for PII likelihood
                    # Extract potential PII from high-similarity sentences
                    words = sentence.split()
                    for word in words:
                        if len(word) > 3 and word.isalnum():
                            # Check if word could be PII
                            word_similarity = self._calculate_word_pii_similarity(word)
                            if word_similarity > 0.4:
                                detected.append({
                                    'type': 'clustered_pii',
                                    'value': word,
                                    'confidence': max_similarity * 0.8,
                                    'method': 'tfidf_clustering',
                                    'similarity_score': word_similarity
                                })
                                        
            return detected
            
        except Exception as e:
            logger.warning(f"TF-IDF clustering error: {e}")
            return []
    
    def _calculate_word_pii_similarity(self, word: str) -> float:
        """Calculate similarity between a word and PII patterns"""
        # Simple heuristics for PII likelihood
        pii_score = 0.0
        
        # Check if word is capitalized (potential name)
        if word[0].isupper() and len(word) > 2:
            pii_score += 0.3
            
        # Check if word contains numbers (potential ID)
        if any(c.isdigit() for c in word):
            pii_score += 0.4
            
        # Check if word contains special characters (potential email, phone)
        if any(c in word for c in '@.-_'):
            pii_score += 0.5
            
        # Check length patterns
        if len(word) in [10, 12, 16]:  # Common ID lengths
            pii_score += 0.3
            
        return min(pii_score, 1.0)
    
    def detect_pii_contextual(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using contextual keyword analysis"""
        detected = []
        
        for category, keywords in self.pii_keywords.items():
            for keyword in keywords:
                if keyword in text.lower():
                    # Look for potential PII values near keywords
                    keyword_pos = text.lower().find(keyword)
                    context_window = text[max(0, keyword_pos-20):keyword_pos+50]
                    
                    # Extract potential PII values (alphanumeric sequences)
                    potential_values = re.findall(r'\b[\w@.-]+\b', context_window)
                    
                    for value in potential_values:
                        if len(value) > 3 and value.lower() != keyword:
                            detected.append({
                                'type': f'contextual_{category}',
                                'value': value,
                                'confidence': 0.6,
                                'method': 'contextual',
                                'keyword': keyword,
                                'context': context_window.strip()
                            })
                            
        return detected
    
    def redact_pii(self, text: str, pii_items: List[Dict[str, Any]]) -> str:
        """Redact detected PII from text"""
        redacted_text = text
        
        # Sort PII items by position (if available) to avoid overlapping replacements
        sorted_items = sorted(pii_items, key=lambda x: x.get('start_pos', 0), reverse=True)
        
        for item in sorted_items:
            pii_type = item['type'].upper()
            placeholder = f"[{pii_type}_REDACTED]"
            
            # Use position-based replacement if available
            if 'start_pos' in item and 'end_pos' in item:
                start = item['start_pos']
                end = item['end_pos']
                redacted_text = redacted_text[:start] + placeholder + redacted_text[end:]
            else:
                # Fallback to string replacement
                redacted_text = redacted_text.replace(item['value'], placeholder)
                
        return redacted_text
    
    def detect_pii_comprehensive(self, text: str) -> Dict[str, Any]:
        """Comprehensive PII detection using all available methods"""
        all_detected = []
        detection_methods = []
        
        # 1. Regex-based detection
        regex_results = self.detect_pii_regex(text)
        if regex_results:
            all_detected.extend(regex_results)
            detection_methods.append('regex')
            
        # 2. spaCy NER detection
        if self.nlp:
            ner_results = self.detect_pii_spacy_ner(text)
            if ner_results:
                all_detected.extend(ner_results)
                detection_methods.append('spacy_ner')
                
        # 3. Contextual keyword detection
        contextual_results = self.detect_pii_contextual(text)
        if contextual_results:
            all_detected.extend(contextual_results)
            detection_methods.append('contextual')
            
        # 4. BERT clustering detection
        if self.sentence_model:
            bert_results = self.detect_pii_bert_clustering(text)
            if bert_results:
                all_detected.extend(bert_results)
                detection_methods.append('bert_clustering')
                
        # 5. TF-IDF clustering detection
        if self.tfidf_vectorizer:
            tfidf_results = self.detect_pii_tfidf_clustering(text)
            if tfidf_results:
                all_detected.extend(tfidf_results)
                detection_methods.append('tfidf_clustering')
        
        # Remove duplicates and calculate overall confidence
        unique_items = self._deduplicate_pii_items(all_detected)
        overall_confidence = self._calculate_overall_confidence(unique_items)
        
        # Generate redacted text
        redacted_text = self.redact_pii(text, unique_items)
        
        return {
            'pii_detected': len(unique_items) > 0,
            'pii_items': unique_items,
            'detection_methods': detection_methods,
            'overall_confidence': overall_confidence,
            'redacted_text': redacted_text,
            'original_text': text,
            'total_methods_used': len(detection_methods)
        }
    
    def _deduplicate_pii_items(self, pii_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate PII items based on value and type"""
        seen = set()
        unique_items = []
        
        for item in pii_items:
            key = (item['value'].lower(), item['type'])
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
                
        return unique_items
    
    def _calculate_overall_confidence(self, pii_items: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        if not pii_items:
            return 0.0
            
        # Weight confidence by detection method
        method_weights = {
            'regex': 1.0,
            'spacy_ner': 0.9,
            'contextual': 0.7,
            'bert_clustering': 0.8,
            'tfidf_clustering': 0.6
        }
        
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for item in pii_items:
            method = item.get('method', 'unknown')
            weight = method_weights.get(method, 0.5)
            confidence = item.get('confidence', 0.0)
            
            total_weighted_confidence += confidence * weight
            total_weight += weight
            
        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0


# Main function for integration with the Flask app
def detect_pii_advanced(text: str) -> Dict[str, Any]:
    """Main function to detect PII using advanced methods"""
    try:
        detector = AdvancedPIIDetector()
        return detector.detect_pii_comprehensive(text)
    except Exception as e:
        logger.error(f"Advanced PII detection failed: {e}")
        # Fallback to basic regex detection
        detector = AdvancedPIIDetector()
        regex_results = detector.detect_pii_regex(text)
        return {
            'pii_detected': len(regex_results) > 0,
            'pii_items': regex_results,
            'detection_methods': ['regex_fallback'],
            'overall_confidence': max([item.get('confidence', 0) for item in regex_results]) if regex_results else 0,
            'redacted_text': detector.redact_pii(text, regex_results),
            'original_text': text,
            'total_methods_used': 1
        }