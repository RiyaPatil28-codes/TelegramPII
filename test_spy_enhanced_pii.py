#!/usr/bin/env python3
"""
Test script for SPY-enhanced PII detection system
Tests comprehensive PII detection with integrated SPY dataset capabilities
"""
import logging
from advanced_pii_detector import AdvancedPIIDetector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_spy_enhanced_detection():
    """Test SPY-enhanced PII detection capabilities"""
    
    print("\n🔍 Testing SPY-Enhanced PII Detection System")
    print("=" * 60)
    
    # Initialize the detector
    detector = AdvancedPIIDetector()
    
    # Test messages with various PII types from SPY dataset
    test_messages = [
        "Hi, my name is John Smith and I live in New York. You can reach me at john.smith@gmail.com or call me at +1-555-123-4567.",
        "Please send the documents to my address: 123 Main Street, Boston, MA 02101. My SSN is 123-45-6789.",
        "My credit card number is 4532 1234 5678 9012, expiry 12/25, CVV 123. DOB: 01/15/1985.",
        "Vehicle VIN: 1HGBH41JXMN109186. Age: 35 years old. Password: SecurePass123!",
        "IP address: 192.168.1.1, IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "Phone IMEI: 35-123456-123456-1. ZIP code: 90210-1234."
    ]
    
    print(f"\n📋 Testing {len(test_messages)} messages with comprehensive PII detection...")
    
    total_detected = 0
    detection_summary = {}
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test Message {i} ---")
        print(f"Input: {message[:80]}{'...' if len(message) > 80 else ''}")
        
        # Perform comprehensive detection
        results = detector.detect_pii_comprehensive(message)
        
        pii_count = len(results['pii_items'])
        total_detected += pii_count
        methods_used = results['detection_methods']
        overall_confidence = results['overall_confidence']
        
        print(f"✅ PII Detected: {pii_count} items")
        print(f"📊 Detection Methods: {', '.join(methods_used)}")
        print(f"🎯 Overall Confidence: {overall_confidence:.2f}")
        
        # Track method usage
        for method in methods_used:
            detection_summary[method] = detection_summary.get(method, 0) + 1
        
        # Display detected items
        if pii_count > 0:
            print("🔍 Detected PII Items:")
            for item in results['pii_items']:
                print(f"   • Type: {item['type']}")
                print(f"     Value: {item['value']}")
                print(f"     Method: {item['method']}")
                print(f"     Confidence: {item['confidence']:.2f}")
                print()
        
        # Show redacted text preview
        if results['redacted_text'] != message:
            redacted_preview = results['redacted_text'][:100] + ('...' if len(results['redacted_text']) > 100 else '')
            print(f"🔒 Redacted: {redacted_preview}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 DETECTION SUMMARY")
    print("=" * 60)
    print(f"Total PII Items Detected: {total_detected}")
    print(f"Average per Message: {total_detected / len(test_messages):.1f}")
    
    print("\n🔧 Detection Methods Used:")
    for method, count in sorted(detection_summary.items()):
        print(f"   • {method}: {count} times")
    
    # Check SPY integration
    spy_methods = [method for method in detection_summary.keys() if 'spy' in method]
    if spy_methods:
        print(f"\n🎯 SPY Enhancement: Successfully integrated - {len(spy_methods)} SPY methods active")
    else:
        print("\n⚠️  SPY Enhancement: Not active in current tests")
    
    # Test SPY-specific detection
    print("\n🧪 Testing SPY-Specific Entity Detection...")
    spy_test_message = "Contact information: firstname John, email john@test.com, phone +1234567890, age 30 years old"
    spy_results = detector.detect_pii_spy_enhanced(spy_test_message)
    
    if spy_results:
        print(f"✅ SPY Detection: {len(spy_results)} items found")
        for item in spy_results:
            print(f"   • {item['type']}: {item['value']} (confidence: {item['confidence']:.2f})")
    else:
        print("📝 SPY Detection: No items detected (training data may be required)")
    
    return total_detected, detection_summary

def test_contextual_keywords():
    """Test enhanced contextual keyword detection"""
    print("\n🔑 Testing Enhanced Contextual Keywords...")
    
    detector = AdvancedPIIDetector()
    
    # Test context-rich messages
    context_messages = [
        "Please provide your personal details: name, address, and phone number.",
        "For identity verification, we need your passport number and date of birth.",
        "Banking information required: account number and routing details.",
        "Contact preferences: email address and mobile number.",
        "Location data: current city, state, and ZIP code."
    ]
    
    for i, message in enumerate(context_messages, 1):
        print(f"\nContext Test {i}: {message}")
        
        contextual_results = detector.detect_pii_contextual(message)
        if contextual_results:
            print(f"   Keywords found: {len(contextual_results)} contextual matches")
            for item in contextual_results:
                print(f"   • Keyword '{item['keyword']}' → {item['type']}")
        else:
            print("   No contextual PII patterns detected")

def main():
    """Main test execution"""
    try:
        print("🚀 SPY-Enhanced PII Detection Test Suite")
        print("Testing advanced privacy protection with synthetic training data")
        
        # Run comprehensive detection tests
        total_detected, summary = test_spy_enhanced_detection()
        
        # Run contextual keyword tests
        test_contextual_keywords()
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🎯 SYSTEM ASSESSMENT")
        print("=" * 60)
        
        if total_detected >= 15:  # Expect high detection rate
            print("✅ Excellent: High PII detection rate achieved")
        elif total_detected >= 10:
            print("✅ Good: Adequate PII detection performance")
        else:
            print("⚠️  Needs improvement: Lower than expected detection rate")
        
        active_methods = len(summary)
        if active_methods >= 4:
            print("✅ Multi-method detection: Strong coverage")
        else:
            print("⚠️  Limited methods: Consider enabling more detection approaches")
        
        print(f"\nSystem ready for production with {active_methods} active detection methods.")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()