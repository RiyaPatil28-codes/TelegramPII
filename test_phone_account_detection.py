#!/usr/bin/env python3
"""
Test script specifically for phone number and account number detection
"""
import logging
from advanced_pii_detector import AdvancedPIIDetector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_phone_number_detection():
    """Test various phone number formats"""
    print("\n📞 Testing Phone Number Detection")
    print("=" * 50)
    
    detector = AdvancedPIIDetector()
    
    phone_test_messages = [
        "Call me at 555-123-4567 tomorrow",
        "My mobile number is (555) 123-4567",
        "Contact: +1-555-123-4567",
        "Phone: +91 9876543210",
        "Reach me on 9876543210",
        "Cell phone: 555.123.4567",
        "International: +44 20 7946 0958",
        "My tel number is 555 123 4567"
    ]
    
    total_detected = 0
    
    for i, message in enumerate(phone_test_messages, 1):
        print(f"\nTest {i}: {message}")
        results = detector.detect_pii_comprehensive(message)
        
        phone_items = [item for item in results['pii_items'] 
                      if 'phone' in item['type'].lower() or 'contact' in item['type'].lower()]
        
        if phone_items:
            total_detected += len(phone_items)
            print(f"✅ Detected {len(phone_items)} phone number(s):")
            for item in phone_items:
                print(f"   • {item['value']} (type: {item['type']}, confidence: {item['confidence']:.2f})")
        else:
            print("❌ No phone numbers detected")
    
    print(f"\n📊 Phone Detection Summary: {total_detected} total phone numbers detected")
    return total_detected

def test_account_number_detection():
    """Test various account number formats"""
    print("\n💳 Testing Account Number Detection")
    print("=" * 50)
    
    detector = AdvancedPIIDetector()
    
    account_test_messages = [
        "My bank account number is 123456789012",
        "Account: 987654321098765",
        "Please transfer to account no 1234567890",
        "Banking details: acc no 98765432101234567",
        "Routing number: 123456789",
        "IBAN: GB82 WEST 1234 5698 7654 32",
        "SWIFT code: DEUTDEFF500",
        "Credit card: 4532 1234 5678 9012",
        "My checking account is 1234567890123456"
    ]
    
    total_detected = 0
    
    for i, message in enumerate(account_test_messages, 1):
        print(f"\nTest {i}: {message}")
        results = detector.detect_pii_comprehensive(message)
        
        account_items = [item for item in results['pii_items'] 
                        if any(keyword in item['type'].lower() for keyword in 
                              ['account', 'bank', 'credit', 'routing', 'iban', 'swift', 'financial'])]
        
        if account_items:
            total_detected += len(account_items)
            print(f"✅ Detected {len(account_items)} financial item(s):")
            for item in account_items:
                print(f"   • {item['value']} (type: {item['type']}, confidence: {item['confidence']:.2f})")
        else:
            print("❌ No account numbers detected")
    
    print(f"\n📊 Account Detection Summary: {total_detected} total financial items detected")
    return total_detected

def test_combined_scenarios():
    """Test messages with both phone numbers and account numbers"""
    print("\n🔄 Testing Combined Phone & Account Detection")
    print("=" * 50)
    
    detector = AdvancedPIIDetector()
    
    combined_messages = [
        "Contact me at 555-123-4567 for account 123456789012 details",
        "Call (555) 987-6543 about my bank account 987654321098",
        "Phone: +1-555-444-3333, Account: 1234567890123456",
        "For questions about account number 98765432101234, call my mobile 9876543210"
    ]
    
    total_phone = 0
    total_account = 0
    
    for i, message in enumerate(combined_messages, 1):
        print(f"\nCombined Test {i}: {message}")
        results = detector.detect_pii_comprehensive(message)
        
        phone_items = [item for item in results['pii_items'] 
                      if 'phone' in item['type'].lower() or 'contact' in item['type'].lower()]
        
        account_items = [item for item in results['pii_items'] 
                        if any(keyword in item['type'].lower() for keyword in 
                              ['account', 'bank', 'financial'])]
        
        total_phone += len(phone_items)
        total_account += len(account_items)
        
        print(f"   📞 Phone items: {len(phone_items)}")
        print(f"   💳 Account items: {len(account_items)}")
        
        for item in phone_items + account_items:
            print(f"   • {item['value']} (type: {item['type']})")
    
    print(f"\n📊 Combined Summary:")
    print(f"   📞 Total phones: {total_phone}")
    print(f"   💳 Total accounts: {total_account}")
    
    return total_phone, total_account

def main():
    """Main test execution"""
    print("🚀 Enhanced Phone & Account Number Detection Test")
    print("Testing comprehensive PII detection capabilities")
    
    try:
        # Run individual tests
        phone_count = test_phone_number_detection()
        account_count = test_account_number_detection()
        combined_phone, combined_account = test_combined_scenarios()
        
        # Overall assessment
        total_phone = phone_count + combined_phone
        total_account = account_count + combined_account
        
        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)
        print(f"📞 Total Phone Numbers Detected: {total_phone}")
        print(f"💳 Total Account Numbers Detected: {total_account}")
        
        # Performance evaluation
        if total_phone >= 8:  # Expect most phone formats to be caught
            print("✅ Excellent phone number detection coverage")
        elif total_phone >= 5:
            print("✅ Good phone number detection")
        else:
            print("⚠️  Phone detection needs improvement")
            
        if total_account >= 8:  # Expect most account formats to be caught
            print("✅ Excellent account number detection coverage")
        elif total_account >= 5:
            print("✅ Good account number detection")
        else:
            print("⚠️  Account detection needs improvement")
        
        overall_score = total_phone + total_account
        if overall_score >= 16:
            print("\n🌟 System ready: Comprehensive PII detection active")
        elif overall_score >= 10:
            print("\n✅ System good: Strong PII detection capabilities")
        else:
            print("\n⚠️  System needs tuning: Detection coverage could be improved")
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()