#!/usr/bin/env python3
"""
Simple PII detection test without MongoDB dependencies
"""

import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class SimplePIIDetector:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+91[\-\s]?)?[0]?(91)?[789]\d{9}'
        self.aadhar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        self.passport_pattern = r'\b[A-Z]{1}[0-9]{7}\b'
        self.credit_card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        self.pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'

    def detect_pii(self, text):
        """Simple PII detection using regex patterns"""
        pii_found = []
        
        # Email detection
        emails = re.findall(self.email_pattern, text)
        for email in emails:
            pii_found.append({
                'type': 'email',
                'value': email,
                'confidence': 0.95,
                'detection_method': 'regex'
            })
        
        # Phone number detection
        phones = re.findall(self.phone_pattern, text)
        for phone_match in phones:
            phone = ''.join(phone_match) if isinstance(phone_match, tuple) else phone_match
            pii_found.append({
                'type': 'phone',
                'value': phone,
                'confidence': 0.90,
                'detection_method': 'regex'
            })
        
        # Aadhar card detection
        aadhars = re.findall(self.aadhar_pattern, text)
        for aadhar in aadhars:
            pii_found.append({
                'type': 'aadhar',
                'value': aadhar,
                'confidence': 0.95,
                'detection_method': 'regex'
            })
        
        # Credit card detection
        cards = re.findall(self.credit_card_pattern, text)
        for card in cards:
            pii_found.append({
                'type': 'credit_card',
                'value': card,
                'confidence': 0.85,
                'detection_method': 'regex'
            })
        
        return pii_found

    def redact_pii(self, text, pii_items):
        """Redact PII from text"""
        redacted_text = text
        
        for pii_item in pii_items:
            if pii_item['type'] == 'email':
                redacted_text = redacted_text.replace(pii_item['value'], '[EMAIL_REDACTED]')
            elif pii_item['type'] == 'phone':
                redacted_text = redacted_text.replace(pii_item['value'], '[PHONE_REDACTED]')
            elif pii_item['type'] == 'aadhar':
                redacted_text = redacted_text.replace(pii_item['value'], '[AADHAR_REDACTED]')
            elif pii_item['type'] == 'credit_card':
                redacted_text = redacted_text.replace(pii_item['value'], '[CARD_REDACTED]')
        
        return redacted_text

def test_pii_detection():
    """Test the PII detection system"""
    detector = SimplePIIDetector()
    
    # Test messages with PII
    test_messages = [
        "My email is john.doe@gmail.com and phone is 9876543210",
        "Contact me at alice@company.com or call +91 8765432109",
        "My Aadhar number is 1234 5678 9012 and credit card is 4532-1234-5678-9012",
        "Hello, how are you today? No PII here!",
        "My passport is A1234567 and PAN is ABCDE1234F"
    ]
    
    print("=== PII Detection Test Results ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        
        # Detect PII
        pii_items = detector.detect_pii(message)
        
        if pii_items:
            print(f"PII Found: {len(pii_items)} items")
            for pii in pii_items:
                print(f"  - {pii['type']}: {pii['value']} (confidence: {pii['confidence']})")
            
            # Show redacted version
            redacted = detector.redact_pii(message, pii_items)
            print(f"Redacted: {redacted}")
        else:
            print("No PII detected")
        
        print("-" * 50)

if __name__ == "__main__":
    test_pii_detection()