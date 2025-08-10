#!/usr/bin/env python3
"""
Simplified Advanced PII Detector - No heavy dependencies
Uses TF-IDF and clustering with scikit-learn only
"""

import re
import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class SimplifiedAdvancedPIIDetector:
    def __init__(self):
        """Initialize simplified advanced PII detector"""
        self.setup_patterns()
        self.setup_pii_keywords()
        self.setup_vectorizer()
        
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
        """Use TF-IDF and clustering to find anomalous terms"""
        try:
            detected = []
            
            # Create a reference corpus of normal text
            normal_corpus = [
                "Hello how are you doing today",
                "The weather is nice and sunny",
                "I enjoy reading books and watching movies", 
                "Thank you for your help and assistance",
                "Have a wonderful day ahead",
                "Nice to meet you and chat",
                "Looking forward to hearing from you",
                "Hope you are doing well"
            ]
            
            # Tokenize input text into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
            
            if not sentences:
                return detected
                
            # Combine corpus with input sentences
            all_texts = normal_corpus + sentences
            
            try:
                # Create TF-IDF matrix
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
                
                # Get vectors for input sentences only
                input_vectors = tfidf_matrix[len(normal_corpus):]
                
                if input_vectors.shape[0] > 1:
                    # Apply DBSCAN clustering to find outliers
                    clustering = DBSCAN(eps=0.5, min_samples=1, metric='cosine')
                    labels = clustering.fit_predict(input_vectors.toarray())
                    
                    # Analyze sentences marked as outliers or in small clusters
                    for i, (sentence, label) in enumerate(zip(sentences, labels)):
                        if self.sentence_has_pii_indicators(sentence):
                            pii_terms = self.extract_pii_terms_from_sentence(sentence)
                            detected.extend(pii_terms)
                            
            except Exception as e:
                logger.warning(f"TF-IDF processing error: {e}")
                
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
        """Extract potential PII terms from a sentence"""
        detected = []
        
        # Extract numeric sequences
        numbers = re.findall(r'\d{4,}', sentence)
        for num in numbers:
            detected.append({
                'type': 'numeric_sequence',
                'value': num,
                'confidence': 0.55,
                'method': 'tfidf_clustering',
                'context': sentence.strip()
            })
            
        # Extract capitalized word sequences (potential names)
        names = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)+\b', sentence)
        for name in names:
            detected.append({
                'type': 'potential_name',
                'value': name,
                'confidence': 0.60,
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
    
    def comprehensive_pii_detection(self, text: str) -> Dict[str, Any]:
        """Run comprehensive PII detection using all available methods"""
        all_detected = []
        
        # Method 1: Enhanced regex detection
        regex_results = self.detect_pii_regex(text)
        all_detected.extend(regex_results)
        
        # Method 2: Advanced contextual detection
        contextual_results = self.detect_pii_contextual_advanced(text)
        all_detected.extend(contextual_results)
        
        # Method 3: TF-IDF clustering
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
            'contextual_advanced': 0.7,
            'tfidf_clustering': 0.6
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