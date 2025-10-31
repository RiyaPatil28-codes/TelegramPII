#!/usr/bin/env python3
"""
Quick test to verify postal code redaction is working
"""

from pii_integration import unified_detector

# Test messages with postal codes
test_messages = [
    "410203",  # The exact message from your screenshot
    "My ZIP code is 90210",
    "I live at postal code SW1A 1AA",
    "PIN code 110001",
    "Send to 10001 New York"
]

print("🔍 Testing Postal Code Redaction")
print("=" * 70)

for msg in test_messages:
    print(f"\n📧 Message: '{msg}'")
    result = unified_detector.analyze_message(msg)
    
    print(f"   Has PII: {result['has_pii']}")
    
    if result['has_pii']:
        print(f"   Detected PII:")
        for pii in result['pii_detected']:
            print(f"      • Type: {pii['type']}")
            print(f"        Value: {pii['value']}")
            print(f"        Confidence: {pii['confidence']:.2f}")
        
        print(f"   Original: {msg}")
        print(f"   Redacted: {result['redacted_message']}")
    else:
        print(f"   ❌ No PII detected")

print("\n" + "=" * 70)
print("✅ Test complete!")
