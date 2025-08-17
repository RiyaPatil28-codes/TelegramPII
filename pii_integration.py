#!/usr/bin/env python3
"""
PII Integration Module - Bridges advanced detection with Flask app
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Try to import the advanced detector
try:
    from advanced_pii_detector import AdvancedPIIDetector
    ADVANCED_DETECTOR_AVAILABLE = True
    logger.info("Advanced PII detector loaded successfully")
except ImportError as e:
    ADVANCED_DETECTOR_AVAILABLE = False
    logger.warning(f"Advanced PII detector not available: {e}")

class UnifiedPIIDetector:
    """Unified PII detector that uses advanced detection if available"""
    
    def __init__(self):
        if ADVANCED_DETECTOR_AVAILABLE:
            self.advanced_detector = AdvancedPIIDetector()
            self.use_advanced = True
            logger.info("Initialized with advanced PII detection")
        else:
            self.use_advanced = False
            logger.info("Initialized with simple regex detection only")
            
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for PII using the best available method"""
        
        if self.use_advanced and ADVANCED_DETECTOR_AVAILABLE:
            try:
                # Use comprehensive advanced detection
                result = self.advanced_detector.detect_pii_comprehensive(message)
                
                # Transform to expected format
                return {
                    'has_pii': result['pii_detected'],
                    'pii_detected': result['pii_items'],
                    'redacted_message': result['redacted_text'],
                    'confidence_score': result['overall_confidence'],
                    'detection_methods': result['detection_methods'],
                    'advanced_detection': True
                }
                
            except Exception as e:
                logger.error(f"Advanced detection failed: {e}, falling back to simple")
                # Fall back to simple detection
                return self._simple_detection(message)
        else:
            return self._simple_detection(message)
    
    def _simple_detection(self, message: str) -> Dict[str, Any]:
        """Simple regex-based PII detection fallback"""
        import re
        
        pii_items = []
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_us_standard': r'\(\d{3}\)\s*\d{3}[-\s]?\d{4}',  # (617) 555-0193
            'phone_us_dashes': r'\d{3}-\d{3}-\d{4}',  # 617-555-0193
            'phone_us_dots': r'\d{3}\.\d{3}\.\d{4}',  # 617.555.0193
            'phone_indian': r'(?:\+91[\-\s]?|0?91[\-\s]?)?[6789]\d{9}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'aadhar': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        }
        
        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, message)
            for match in matches:
                pii_items.append({
                    'type': pii_type,
                    'value': match.strip(),
                    'confidence': 0.9
                })
        
        # Generate redacted message
        redacted = message
        for item in pii_items:
            placeholder = f"[{item['type'].upper()}_REDACTED]"
            redacted = redacted.replace(item['value'], placeholder)
        
        return {
            'has_pii': len(pii_items) > 0,
            'pii_detected': pii_items,
            'redacted_message': redacted,
            'confidence_score': max([item['confidence'] for item in pii_items]) if pii_items else 0,
            'detection_methods': ['regex'],
            'advanced_detection': False
        }

# Create a global instance
unified_detector = UnifiedPIIDetector()