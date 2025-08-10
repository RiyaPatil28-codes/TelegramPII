#!/usr/bin/env python3
"""
Advanced PII Detector with BERT, TF-IDF, and Unsupervised Learning
"""

import re
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModel
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class AdvancedPIIDetector:
    def __init__(self):
        """Initialize advanced PII detector with BERT and unsupervised learning"""
        self.setup_models()
        self.setup_patterns()
        self.setup_pii_keywords()
        
    def setup_models(self):
        """Initialize BERT and sentence transformer models"""
        try:
            # Use lightweight BERT model for PII context detection
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model")
            
            # TF-IDF vectorizer for text analysis
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=1
            )
            
        except Exception as e:
            logger.warning(f"Model loading error: {e}. Using fallback models.")
            self.sentence_model = None
            
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
    
    def detect_pii_contextual(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using contextual keyword analysis"""
        detected = []
        words = text.lower().split()
        
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
    
    def detect_pii_bert_clustering(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using BERT embeddings and unsupervised clustering"""
        if not self.sentence_model:
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
            clustering = DBSCAN(eps=0.3, min_samples=1, metric='cosine')
            clusters = clustering.fit_predict(embeddings)
            
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
    
    def detect_pii_tfidf_anomaly(self, text: str, corpus: List[str] = None) -> List[Dict[str, Any]]:
        """Detect PII using TF-IDF anomaly detection"""
        try:
            detected = []
            
            # Create corpus for comparison (use common non-PII text if no corpus provided)
            if not corpus:
                corpus = [
                    "Hello how are you doing today",
                    "The weather is nice outside",
                    "I like reading books and watching movies",
                    "Thank you for your help",
                    "Have a great day ahead"
                ]
            
            # Add current text to corpus
            all_texts = corpus + [text]
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Get TF-IDF scores for the input text (last item)
            text_vector = tfidf_matrix[-1]
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Find high-scoring terms that might indicate PII
            text_scores = text_vector.toarray()[0]
            high_score_indices = np.where(text_scores > 0.1)[0]  # Threshold for significance
            
            for idx in high_score_indices:
                term = feature_names[idx]
                score = text_scores[idx]
                
                # Check if high-scoring term matches PII patterns
                if self._is_potential_pii_term(term, score):
                    detected.append({
                        'type': 'anomaly_term',
                        'value': term,
                        'confidence': min(0.9, score * 1.2),
                        'method': 'tfidf_anomaly',
                        'tfidf_score': score
                    })
                    
            return detected
            
        except Exception as e:
            logger.warning(f"TF-IDF anomaly detection error: {e}")
            return []
    
    def _is_potential_pii_term(self, term: str, tfidf_score: float) -> bool:
        """Check if a term with high TF-IDF score is potentially PII"""
        # Check against known PII patterns
        for pattern in self.pii_patterns.values():
            if re.match(pattern, term, re.IGNORECASE):
                return True
                
        # Check for numeric sequences (potential IDs, phone numbers, etc.)
        if re.match(r'^\d+$', term) and len(term) >= 6:
            return True
            
        # Check for email-like patterns
        if '@' in term or '.' in term:
            return True
            
        # Check for capitalized sequences (potential names)
        if re.match(r'^[A-Z][a-z]+$', term) and tfidf_score > 0.3:
            return True
            
        return False
    
    def comprehensive_pii_detection(self, text: str, corpus: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive PII detection using all methods"""
        all_detected = []
        
        # Method 1: Regex-based detection (high precision)
        regex_results = self.detect_pii_regex(text)
        all_detected.extend(regex_results)
        
        # Method 2: Contextual keyword detection
        contextual_results = self.detect_pii_contextual(text)
        all_detected.extend(contextual_results)
        
        # Method 3: BERT clustering (if available)
        if self.sentence_model:
            bert_results = self.detect_pii_bert_clustering(text)
            all_detected.extend(bert_results)
        
        # Method 4: TF-IDF anomaly detection
        tfidf_results = self.detect_pii_tfidf_anomaly(text, corpus)
        all_detected.extend(tfidf_results)
        
        # Deduplicate and consolidate results
        consolidated_results = self._consolidate_detections(all_detected)
        
        # Calculate overall confidence score
        overall_confidence = self._calculate_overall_confidence(consolidated_results)
        
        return {
            'text': text,
            'pii_detected': len(consolidated_results) > 0,
            'pii_items': consolidated_results,
            'detection_methods': self._get_methods_used(consolidated_results),
            'overall_confidence': overall_confidence,
            'redacted_text': self._redact_text(text, consolidated_results)
        }
    
    def _consolidate_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate overlapping detections and remove duplicates"""
        if not detections:
            return []
            
        consolidated = []
        seen_values = set()
        
        # Sort by confidence (highest first)
        sorted_detections = sorted(detections, key=lambda x: x.get('confidence', 0), reverse=True)
        
        for detection in sorted_detections:
            value = detection['value'].lower().strip()
            
            # Skip if already seen (avoid duplicates)
            if value in seen_values:
                continue
                
            # Skip very short or common values
            if len(value) < 3 or value in ['the', 'and', 'for', 'you', 'are']:
                continue
                
            seen_values.add(value)
            consolidated.append(detection)
            
        return consolidated
    
    def _calculate_overall_confidence(self, detections: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for PII detection"""
        if not detections:
            return 0.0
            
        # Weight confidence scores by detection method reliability
        method_weights = {
            'regex': 1.0,
            'contextual': 0.7,
            'bert_ner': 0.8,
            'bert_location': 0.6,
            'tfidf_anomaly': 0.5
        }
        
        weighted_scores = []
        for detection in detections:
            method = detection.get('method', 'unknown')
            confidence = detection.get('confidence', 0)
            weight = method_weights.get(method, 0.5)
            weighted_scores.append(confidence * weight)
            
        return min(0.95, np.mean(weighted_scores))
    
    def _get_methods_used(self, detections: List[Dict[str, Any]]) -> List[str]:
        """Get list of detection methods used"""
        methods = set()
        for detection in detections:
            methods.add(detection.get('method', 'unknown'))
        return list(methods)
    
    def _redact_text(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Redact PII from text"""
        redacted = text
        
        # Sort by position to avoid offset issues
        sorted_detections = sorted(
            [d for d in detections if 'start_pos' in d], 
            key=lambda x: x.get('start_pos', 0), 
            reverse=True
        )
        
        # Redact using placeholders
        for detection in sorted_detections:
            value = detection['value']
            pii_type = detection['type']
            placeholder = f"[{pii_type.upper()}_REDACTED]"
            redacted = redacted.replace(value, placeholder)
            
        return redacted

# Global instance
advanced_detector = AdvancedPIIDetector()

def detect_pii_advanced(text: str, corpus: List[str] = None) -> Dict[str, Any]:
    """Main function to detect PII using advanced methods"""
    return advanced_detector.comprehensive_pii_detection(text, corpus)

if __name__ == "__main__":
    # Test the advanced PII detector
    test_text = "Hi, I'm John Smith from Mumbai. My email is john.smith@gmail.com and phone is 9876543210. My Aadhar is 1234-5678-9012."
    
    result = detect_pii_advanced(test_text)
    
    print("Advanced PII Detection Results:")
    print(f"Text: {result['text']}")
    print(f"PII Detected: {result['pii_detected']}")
    print(f"Overall Confidence: {result['overall_confidence']:.2f}")
    print(f"Methods Used: {result['detection_methods']}")
    print(f"Redacted Text: {result['redacted_text']}")
    print("\nDetected PII Items:")
    for item in result['pii_items']:
        print(f"  - {item['type']}: {item['value']} (confidence: {item['confidence']:.2f}, method: {item['method']})")