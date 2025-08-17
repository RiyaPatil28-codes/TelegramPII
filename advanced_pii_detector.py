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

# Import training dataset
try:
    from pii_training_dataset import get_training_corpus, get_sensitive_patterns, get_pii_keywords
    TRAINING_DATASET_AVAILABLE = True
except ImportError:
    TRAINING_DATASET_AVAILABLE = False

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
            
        # Initialize TF-IDF and clustering models with training data
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1500,
                    stop_words='english',
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.8
                )
                
                # Train TF-IDF on unlabeled dataset if available
                if TRAINING_DATASET_AVAILABLE:
                    training_corpus = get_training_corpus()
                    self.tfidf_vectorizer.fit(training_corpus)
                    logger.info(f"✓ Trained TF-IDF vectorizer on {len(training_corpus)} unlabeled samples")
                    
                    # Store training vectors for similarity comparison
                    self.training_vectors = self.tfidf_vectorizer.transform(training_corpus)
                    
                    # Store sensitive patterns for clustering reference
                    self.sensitive_patterns = get_sensitive_patterns()
                    self.pii_keywords_extended = get_pii_keywords()
                else:
                    self.training_vectors = None
                    self.sensitive_patterns = []
                    self.pii_keywords_extended = []
                
                self.dbscan_model = DBSCAN(eps=0.4, min_samples=2, metric='cosine')
                self.kmeans_model = KMeans(n_clusters=5, random_state=42, n_init=10)
                logger.info("✓ Loaded scikit-learn models (TF-IDF, DBSCAN, K-Means)")
            except Exception as e:
                logger.warning(f"Failed to load scikit-learn models: {e}")
                self.tfidf_vectorizer = None
                self.dbscan_model = None
                self.kmeans_model = None
                self.training_vectors = None
        else:
            logger.warning("scikit-learn not available")
            self.tfidf_vectorizer = None
            self.dbscan_model = None
            self.kmeans_model = None
            self.training_vectors = None
            
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
        """Enhanced TF-IDF clustering with pre-trained unsupervised model"""
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
                
            if len(sentences) == 0:
                return detected
                
            # Transform input sentences using pre-trained TF-IDF
            sentence_vectors = self.tfidf_vectorizer.transform(sentences)
            
            # Method 1: Compare with training corpus if available
            if self.training_vectors is not None:
                # Calculate similarity with training data
                training_similarities = cosine_similarity(sentence_vectors, self.training_vectors)
                max_training_similarities = np.max(training_similarities, axis=1)
                
                for i, sentence in enumerate(sentences):
                    similarity_score = max_training_similarities[i]
                    
                    if similarity_score > 0.25:  # Lower threshold for trained model
                        # Apply clustering to identify PII patterns
                        sentence_features = sentence_vectors[i:i+1]
                        
                        # Use K-means to find closest cluster center
                        if len(sentences) > 1:
                            all_vectors = np.vstack([sentence_vectors.toarray(), 
                                                   self.training_vectors[:50].toarray()])  # Sample training data
                            
                            clusters = self.kmeans_model.fit_predict(all_vectors)
                            sentence_cluster = clusters[i]
                            
                            # Check if sentence clusters with PII-like training data
                            training_clusters = clusters[len(sentences):]
                            cluster_pii_likelihood = self._calculate_cluster_pii_likelihood(
                                sentence_cluster, training_clusters
                            )
                            
                            if cluster_pii_likelihood > 0.3:
                                # Extract potential PII from sentence
                                pii_candidates = self._extract_pii_candidates_from_sentence(
                                    sentence, similarity_score, cluster_pii_likelihood
                                )
                                detected.extend(pii_candidates)
            
            # Method 2: Keyword-based clustering for fallback
            if len(detected) == 0 and len(sentences) >= 2:
                # Use extended PII keywords from training dataset
                pii_keywords = (list(self.pii_keywords_extended) if self.pii_keywords_extended 
                              else [kw for kwlist in self.pii_keywords.values() for kw in kwlist])
                
                # Create keyword vectors
                keyword_vectors = self.tfidf_vectorizer.transform(pii_keywords)
                
                # Calculate similarities
                keyword_similarities = cosine_similarity(sentence_vectors, keyword_vectors)
                max_keyword_similarities = np.max(keyword_similarities, axis=1)
                
                # Apply DBSCAN clustering to sentences
                if sentence_vectors.shape[0] > 1:
                    clusters = self.dbscan_model.fit_predict(sentence_vectors.toarray())
                    
                    for i, sentence in enumerate(sentences):
                        if (max_keyword_similarities[i] > 0.2 and 
                            clusters[i] != -1):  # Not noise cluster
                            
                            # Extract PII candidates with clustering confidence
                            confidence_boost = min(max_keyword_similarities[i] * 1.2, 0.9)
                            candidates = self._extract_pii_candidates_from_sentence(
                                sentence, max_keyword_similarities[i], confidence_boost
                            )
                            detected.extend(candidates)
                            
            return detected
            
        except Exception as e:
            logger.warning(f"Enhanced TF-IDF clustering error: {e}")
            return []
    
    def _calculate_cluster_pii_likelihood(self, sentence_cluster: int, training_clusters: np.ndarray) -> float:
        """Calculate likelihood that a cluster contains PII based on training data"""
        if len(training_clusters) == 0:
            return 0.0
            
        # Count how many training samples are in the same cluster
        same_cluster_count = np.sum(training_clusters == sentence_cluster)
        total_training_samples = len(training_clusters)
        
        # Higher likelihood if more training samples share the cluster
        likelihood = same_cluster_count / total_training_samples
        return min(likelihood * 2.0, 1.0)  # Boost and cap at 1.0
    
    def _extract_pii_candidates_from_sentence(self, sentence: str, similarity_score: float, 
                                            confidence_boost: float) -> List[Dict[str, Any]]:
        """Extract PII candidates from a sentence with clustering analysis"""
        candidates = []
        words = sentence.split()
        
        for word in words:
            if len(word) <= 2:
                continue
                
            # Calculate word-level PII likelihood
            word_pii_score = self._calculate_word_pii_similarity(word)
            
            # Enhanced scoring with clustering information
            combined_confidence = (word_pii_score * 0.4 + 
                                 similarity_score * 0.3 + 
                                 confidence_boost * 0.3)
            
            if combined_confidence > 0.35:
                # Determine PII type based on word characteristics
                pii_type = self._classify_pii_type_advanced(word, sentence)
                
                candidates.append({
                    'type': f'ml_clustered_{pii_type}',
                    'value': word,
                    'confidence': min(combined_confidence, 0.85),
                    'method': 'tfidf_clustering_trained',
                    'similarity_score': similarity_score,
                    'clustering_boost': confidence_boost,
                    'context': sentence[:50] + '...' if len(sentence) > 50 else sentence
                })
                
        return candidates
    
    def _classify_pii_type_advanced(self, word: str, context: str) -> str:
        """Classify PII type using advanced heuristics"""
        word_lower = word.lower()
        context_lower = context.lower()
        
        # Email patterns
        if '@' in word or 'email' in context_lower:
            return 'email'
        
        # Phone patterns  
        if (any(c.isdigit() for c in word) and len(word) >= 8) or 'phone' in context_lower:
            return 'phone'
            
        # Name patterns
        if (word[0].isupper() and word.isalpha() and 
            any(indicator in context_lower for indicator in ['name', 'called', 'mr', 'ms', 'dr'])):
            return 'name'
            
        # Location patterns
        if (word[0].isupper() and 
            any(indicator in context_lower for indicator in ['live', 'from', 'in', 'at', 'city', 'state'])):
            return 'location'
            
        # Financial patterns
        if (any(c.isdigit() for c in word) and 
            any(indicator in context_lower for indicator in ['account', 'card', 'bank', 'pay'])):
            return 'financial'
            
        # ID patterns
        if (any(c.isdigit() for c in word) and len(word) >= 6 and
            any(indicator in context_lower for indicator in ['id', 'number', 'license', 'passport'])):
            return 'identification'
            
        return 'personal_info'
    
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