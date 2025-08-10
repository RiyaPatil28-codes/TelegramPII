import re
import spacy
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
import numpy as np
from datetime import datetime

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    logging.warning("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
    nlp = None

class PIIDetector:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+91[\-\s]?)?[0]?(91)?[789]\d{9}'
        self.aadhar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        self.passport_pattern = r'\b[A-Z]{1}[0-9]{7}\b'
        self.credit_card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        self.pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # PII keywords for clustering
        self.pii_keywords = [
            'name', 'phone', 'email', 'address', 'aadhar', 'passport', 'ssn',
            'credit card', 'debit card', 'pan', 'bank account', 'license',
            'birth date', 'dob', 'age', 'location', 'zip code', 'pincode'
        ]
    
    def detect_regex_pii(self, text):
        """Detect PII using regex patterns"""
        pii_found = []
        
        # Email detection
        emails = re.findall(self.email_pattern, text)
        if emails:
            pii_found.extend([{'type': 'email', 'value': email, 'confidence': 0.95} for email in emails])
        
        # Phone number detection
        phones = re.findall(self.phone_pattern, text)
        if phones:
            pii_found.extend([{'type': 'phone', 'value': phone, 'confidence': 0.9} for phone in phones])
        
        # Aadhar number detection
        aadhar_numbers = re.findall(self.aadhar_pattern, text)
        if aadhar_numbers:
            pii_found.extend([{'type': 'aadhar', 'value': aadhar.replace(' ', ''), 'confidence': 0.85} for aadhar in aadhar_numbers])
        
        # Passport number detection
        passport_numbers = re.findall(self.passport_pattern, text)
        if passport_numbers:
            pii_found.extend([{'type': 'passport', 'value': passport, 'confidence': 0.8} for passport in passport_numbers])
        
        # Credit card detection
        credit_cards = re.findall(self.credit_card_pattern, text)
        if credit_cards:
            pii_found.extend([{'type': 'credit_card', 'value': card.replace(' ', '').replace('-', ''), 'confidence': 0.9} for card in credit_cards])
        
        # PAN number detection
        pan_numbers = re.findall(self.pan_pattern, text)
        if pan_numbers:
            pii_found.extend([{'type': 'pan', 'value': pan, 'confidence': 0.85} for pan in pan_numbers])
        
        return pii_found
    
    def detect_ner_pii(self, text):
        """Detect PII using Named Entity Recognition"""
        if not nlp:
            return []
        
        pii_found = []
        doc = nlp(text)
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY', 'CARDINAL']:
                confidence = 0.7
                if ent.label_ == 'PERSON':
                    confidence = 0.8
                elif ent.label_ == 'DATE':
                    confidence = 0.6
                
                pii_found.append({
                    'type': ent.label_.lower(),
                    'value': ent.text,
                    'confidence': confidence
                })
        
        return pii_found
    
    def detect_clustering_pii(self, text):
        """Detect PII using clustering approach"""
        words = text.lower().split()
        pii_found = []
        
        # Check for PII-related keywords
        for word in words:
            for keyword in self.pii_keywords:
                if keyword in word or word in keyword:
                    # Look for potential PII values near keywords
                    word_index = words.index(word)
                    context_window = 3  # Look 3 words before and after
                    
                    start_idx = max(0, word_index - context_window)
                    end_idx = min(len(words), word_index + context_window + 1)
                    
                    context = ' '.join(words[start_idx:end_idx])
                    
                    # Use regex to find potential PII in context
                    regex_results = self.detect_regex_pii(context)
                    if regex_results:
                        for result in regex_results:
                            result['confidence'] *= 0.8  # Lower confidence for clustering method
                            pii_found.append(result)
        
        return pii_found
    
    def redact_pii(self, text, pii_items):
        """Redact PII from text"""
        redacted_text = text
        
        for pii_item in pii_items:
            pii_value = pii_item['value']
            pii_type = pii_item['type']
            
            # Create redaction based on type
            if pii_type == 'email':
                redaction = '[EMAIL_REDACTED]'
            elif pii_type == 'phone':
                redaction = '[PHONE_REDACTED]'
            elif pii_type == 'aadhar':
                redaction = '[AADHAR_REDACTED]'
            elif pii_type == 'passport':
                redaction = '[PASSPORT_REDACTED]'
            elif pii_type == 'credit_card':
                redaction = '[CARD_REDACTED]'
            elif pii_type == 'pan':
                redaction = '[PAN_REDACTED]'
            elif pii_type == 'person':
                redaction = '[NAME_REDACTED]'
            else:
                redaction = f'[{pii_type.upper()}_REDACTED]'
            
            redacted_text = redacted_text.replace(pii_value, redaction)
        
        return redacted_text
    
    def detect_all_pii(self, text):
        """Detect PII using all methods and combine results"""
        all_pii = []
        
        # Detect using regex
        regex_pii = self.detect_regex_pii(text)
        all_pii.extend(regex_pii)
        
        # Detect using NER
        ner_pii = self.detect_ner_pii(text)
        all_pii.extend(ner_pii)
        
        # Detect using clustering approach
        clustering_pii = self.detect_clustering_pii(text)
        all_pii.extend(clustering_pii)
        
        # Remove duplicates and merge similar detections
        unique_pii = []
        seen_values = set()
        
        for pii_item in all_pii:
            value = pii_item['value'].lower().strip()
            if value not in seen_values and len(value) > 1:
                seen_values.add(value)
                unique_pii.append(pii_item)
        
        # Sort by confidence
        unique_pii.sort(key=lambda x: x['confidence'], reverse=True)
        
        logging.debug(f"Detected PII: {unique_pii}")
        return unique_pii
    
    def analyze_message(self, message_text):
        """Analyze message for PII and return detailed results"""
        pii_detected = self.detect_all_pii(message_text)
        
        has_pii = len(pii_detected) > 0
        redacted_message = self.redact_pii(message_text, pii_detected) if has_pii else None
        
        analysis_result = {
            'original_message': message_text,
            'has_pii': has_pii,
            'pii_detected': pii_detected,
            'redacted_message': redacted_message,
            'confidence_score': max([pii['confidence'] for pii in pii_detected]) if pii_detected else 0,
            'analysis_timestamp': datetime.utcnow()
        }
        
        return analysis_result

# Global PII detector instance
pii_detector = PIIDetector()
