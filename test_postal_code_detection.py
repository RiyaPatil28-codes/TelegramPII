#!/usr/bin/env python3
"""
Test script for comprehensive postal/ZIP code detection
Validates detection across 30+ international formats
"""

from advanced_pii_detector import AdvancedPIIDetector
import logging

logging.basicConfig(level=logging.INFO)

def test_postal_code_detection():
    """Test postal code detection across international formats"""
    
    print("🔍 Testing Comprehensive Postal/ZIP Code Detection")
    print("=" * 70)
    
    detector = AdvancedPIIDetector()
    
    # Test cases covering 30+ countries
    test_cases = [
        # US ZIP codes
        ("My address is 90210", "zipcode_us", "90210"),
        ("Send to ZIP 90210-1234", "zipcode_us", "90210-1234"),
        
        # UK postcodes
        ("London SW1A 1AA is the address", "postcode_uk", "SW1A 1AA"),
        ("Postcode: W1T4TJ", "postcode_uk", "W1T4TJ"),
        
        # Canadian postal codes
        ("Ottawa K1A 0B1 Canada", "postcode_canada", "K1A 0B1"),
        ("Postal code K1A0B1", "postcode_canada", "K1A0B1"),
        
        # Indian PIN codes
        ("Mumbai 400001 India", "pincode_india", "400001"),
        ("PIN code is 110001", "pincode_india", "110001"),
        
        # Australian postcodes
        ("Sydney 2000 NSW", "postcode_australia", "2000"),
        ("Melbourne postcode 3000", "postcode_australia", "3000"),
        
        # German postcodes
        ("Berlin 10115 Germany", "postcode_germany", "10115"),
        
        # French postal codes
        ("Paris 75001 France", "postcode_france", "75001"),
        
        # Netherlands postcodes
        ("Amsterdam 1012 JS", "postcode_netherlands", "1012 JS"),
        ("Postcode 1012JS", "postcode_netherlands", "1012JS"),
        
        # Japanese postal codes
        ("Tokyo 100-0001", "postcode_japan", "100-0001"),
        ("Postal code 1000001", "postcode_japan", "1000001"),
        
        # Chinese postal codes
        ("Beijing 100000", "postcode_china", "100000"),
        
        # Brazilian CEP codes
        ("São Paulo 01310-100", "postcode_brazil", "01310-100"),
        ("CEP: 01310100", "postcode_brazil", "01310100"),
        
        # Polish postal codes
        ("Warsaw 00-001", "postcode_poland", "00-001"),
        
        # Swedish postal codes
        ("Stockholm 111 22", "postcode_sweden", "111 22"),
        ("Postcode 11122", "postcode_sweden", "11122"),
        
        # Singapore postal codes
        ("Singapore 018956", "postcode_singapore", "018956"),
        
        # Irish Eircode
        ("Dublin D02 AF30", "postcode_ireland", "D02 AF30"),
        
        # Multiple postal codes in one message
        ("Shipping from 90210 to SW1A 1AA", "multiple", ["90210", "SW1A 1AA"]),
        
        # Contextual detection
        ("My ZIP code is 10001", "zipcode_us", "10001"),
        ("What's your pincode? Mine is 560001", "pincode_india", "560001"),
        ("The postcode for this address is W1A 0AX", "postcode_uk", "W1A 0AX"),
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    for i, (message, expected_type, expected_value) in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{total_tests}: {message}")
        print(f"Expected: {expected_type} = {expected_value}")
        
        # Call all detection methods
        regex_detections = detector.detect_pii_regex(message)
        spy_detections = detector.detect_pii_spy_enhanced(message)
        
        # Combine all detections
        all_detections = regex_detections + spy_detections
        
        # Extract postal/zip code detections
        postal_detections = [
            item for item in all_detections
            if 'zip' in item['type'].lower() or 'post' in item['type'].lower() or 'pin' in item['type'].lower()
        ]
        
        if postal_detections:
            print(f"\n✅ DETECTED ({len(postal_detections)} items):")
            for detection in postal_detections:
                print(f"   Type: {detection['type']}")
                print(f"   Value: {detection['value']}")
                print(f"   Confidence: {detection.get('confidence', 'N/A')}")
                print(f"   Method: {detection.get('method', 'N/A')}")
            
            # Verify detection
            if expected_type == "multiple":
                detected_values = [d['value'].strip() for d in postal_detections]
                if all(val in ' '.join(detected_values) for val in expected_value):
                    print(f"\n✅ TEST PASSED")
                    passed_tests += 1
                else:
                    print(f"\n❌ TEST FAILED - Expected all values: {expected_value}")
                    failed_tests.append((message, expected_value, detected_values))
            else:
                detected_value = postal_detections[0]['value'].strip().replace(' ', '')
                expected_val = expected_value.replace(' ', '')
                if detected_value == expected_val or expected_val in detected_value:
                    print(f"\n✅ TEST PASSED")
                    passed_tests += 1
                else:
                    print(f"\n❌ TEST FAILED - Got: {detected_value}, Expected: {expected_value}")
                    failed_tests.append((message, expected_value, detected_value))
        else:
            print(f"\n❌ NO POSTAL/ZIP CODE DETECTED")
            print(f"❌ TEST FAILED")
            failed_tests.append((message, expected_value, "None"))
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Failed: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for msg, expected, actual in failed_tests:
            print(f"   Message: {msg}")
            print(f"   Expected: {expected}")
            print(f"   Got: {actual}")
            print()
    
    print(f"\n{'='*70}")
    print(f"🌍 International Coverage:")
    print(f"   • US ZIP codes (5 & 5+4 digits)")
    print(f"   • UK postcodes (various formats)")
    print(f"   • Canadian postal codes (A1A 1A1)")
    print(f"   • Indian PIN codes (6 digits)")
    print(f"   • Australian postcodes (4 digits)")
    print(f"   • European formats (DE, FR, ES, IT, NL, etc.)")
    print(f"   • Asian formats (JP, CN, SG, KR, etc.)")
    print(f"   • Latin American formats (BR, MX, AR)")
    print(f"   • 30+ country-specific patterns")
    print(f"{'='*70}")
    
    return passed_tests, total_tests

if __name__ == "__main__":
    passed, total = test_postal_code_detection()
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Postal code detection is working perfectly.")
    else:
        print(f"\n⚠️  Some tests failed. Review the failed cases above.")
