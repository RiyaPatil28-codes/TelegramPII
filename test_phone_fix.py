#!/usr/bin/env python3
"""
Test enhanced phone number detection
"""

from advanced_pii_detector import AdvancedPIIDetector

def test_phone_detection():
    detector = AdvancedPIIDetector()
    
    test_messages = [
        "text me at (617) 555-0193 because I'm seriously about to lose it",
        "Call me at 617-555-0193 for more details",
        "My number is 617.555.0193",
        "Reach me on +1 617 555 0193",
        "Phone: (617) 555-0193",
        "Contact: 6175550193"
    ]
    
    print("Testing Enhanced Phone Number Detection:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message}")
        result = detector.detect_pii_comprehensive(message)
        
        phone_detections = [item for item in result['pii_items'] if 'phone' in item['type']]
        if phone_detections:
            print(f"✓ DETECTED: {len(phone_detections)} phone number(s)")
            for detection in phone_detections:
                print(f"  - Type: {detection['type']}, Value: {detection['value']}, Confidence: {detection['confidence']}")
        else:
            print("✗ NO PHONE NUMBERS DETECTED")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_phone_detection()