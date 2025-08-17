#!/usr/bin/env python3
"""
Comprehensive test for international phone number detection across all countries
"""

from pii_integration import unified_detector

# Comprehensive test cases for international phone numbers
test_cases = {
    'United States': [
        '(617) 555-0193',
        '617-555-0193', 
        '617.555.0193',
        '+1 617 555 0193',
        '1-617-555-0193'
    ],
    'United Kingdom': [
        '+44 20 7946 0958',
        '020 7946 0958',
        '+44 1234 567890'
    ],
    'India': [
        '+91 98765 43210',
        '9876543210',
        '+91 98765 43210'
    ],
    'China': [
        '+86 138 0013 8000',
        '138 0013 8000'
    ],
    'Germany': [
        '+49 30 12345678',
        '030 12345678'
    ],
    'France': [
        '+33 1 42 34 56 78',
        '01 42 34 56 78'
    ],
    'Japan': [
        '+81 90 1234 5678',
        '090-1234-5678'
    ],
    'Australia': [
        '+61 2 9876 5432',
        '02 9876 5432'
    ],
    'Brazil': [
        '+55 11 99999 8888',
        '11 99999-8888'
    ],
    'Russia': [
        '+7 495 123 45 67',
        '8 495 123 45 67'
    ],
    'Canada': [
        '+1 416 555 1234',
        '416-555-1234'
    ],
    'Mexico': [
        '+52 55 1234 5678',
        '55 1234 5678'
    ],
    'South Korea': [
        '+82 10 1234 5678',
        '010-1234-5678'
    ],
    'Spain': [
        '+34 6 1234 5678',
        '612 345 678'
    ],
    'Italy': [
        '+39 123 456 7890',
        '123 456 7890'
    ]
}

def test_comprehensive_phone_detection():
    """Test phone number detection across all major countries"""
    print("=== Comprehensive International Phone Number Detection Test ===\n")
    
    total_tested = 0
    total_detected = 0
    country_results = {}
    
    for country, phone_numbers in test_cases.items():
        print(f"Testing {country}:")
        detected_in_country = 0
        
        for phone in phone_numbers:
            test_message = f"Please call me at {phone} for urgent matters"
            result = unified_detector.analyze_message(test_message)
            
            # Check if any phone number was detected
            phone_items = [item for item in result['pii_detected'] 
                          if 'phone' in item['type'].lower()]
            
            if phone_items:
                print(f"  ✓ {phone} → Detected as {phone_items[0]['type']}")
                detected_in_country += 1
            else:
                print(f"  ✗ {phone} → Not detected")
            
            total_tested += 1
        
        total_detected += detected_in_country
        country_results[country] = (detected_in_country, len(phone_numbers))
        print(f"  → {detected_in_country}/{len(phone_numbers)} detected\n")
    
    # Summary
    print("=" * 60)
    print("DETECTION SUMMARY:")
    print("=" * 60)
    
    for country, (detected, total) in country_results.items():
        success_rate = (detected / total) * 100
        print(f"{country:20}: {detected:2}/{total} ({success_rate:5.1f}%)")
    
    overall_success = (total_detected / total_tested) * 100
    print("-" * 60)
    print(f"{'OVERALL':20}: {total_detected:2}/{total_tested} ({overall_success:5.1f}%)")
    print("=" * 60)
    
    if overall_success >= 90:
        print("🎉 EXCELLENT: International phone detection is working brilliantly!")
    elif overall_success >= 75:
        print("✅ GOOD: Most international phone numbers are being detected")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Detection rate could be better")
    
    return total_detected, total_tested

if __name__ == "__main__":
    test_comprehensive_phone_detection()