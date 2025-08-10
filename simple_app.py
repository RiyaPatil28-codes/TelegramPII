#!/usr/bin/env python3
"""
Simple Flask app for PII detection without MongoDB dependencies
"""
import os
import re
import json
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_for_pii_testing")

class SimplePIIDetector:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(?:\+91[\-\s]?|0?91[\-\s]?)?[789]\d{9}'
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
        for phone in phones:
            if phone.strip():  # Only add non-empty phone numbers
                pii_found.append({
                    'type': 'phone',
                    'value': phone.strip(),
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
        
        # PAN card detection
        pans = re.findall(self.pan_pattern, text)
        for pan in pans:
            pii_found.append({
                'type': 'pan_card',
                'value': pan,
                'confidence': 0.90,
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
            elif pii_item['type'] == 'pan_card':
                redacted_text = redacted_text.replace(pii_item['value'], '[PAN_REDACTED]')
        
        return redacted_text

# Initialize PII detector
pii_detector = SimplePIIDetector()

@app.route('/')
def index():
    """Simple home page for testing PII detection"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PII Detection Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .test-area { margin: 20px 0; }
            textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; min-height: 100px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px 0 0; }
            button:hover { background: #0056b3; }
            .results { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }
            .pii-item { background: #fff3cd; padding: 8px; margin: 5px 0; border-left: 3px solid #ffc107; }
            .no-pii { color: #28a745; }
            .redacted { background: #e7f3ff; padding: 10px; border-left: 3px solid #007bff; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 PII Detection System Test</h1>
            
            <div class="test-area">
                <h3>Enter text to test PII detection:</h3>
                <textarea id="testText" placeholder="Try: My email is john@example.com and phone is 9876543210"></textarea>
                <br>
                <button onclick="detectPII()">🔍 Detect PII</button>
                <button onclick="clearResults()">🗑️ Clear</button>
            </div>
            
            <div id="results" class="results" style="display:none;">
                <h4>Detection Results:</h4>
                <div id="piiResults"></div>
                <div id="redactedResults"></div>
            </div>
            
            <div class="test-area">
                <h3>Sample test cases:</h3>
                <button onclick="testEmail()">Email Test</button>
                <button onclick="testPhone()">Phone Test</button>
                <button onclick="testAadhar()">Aadhar Test</button>
                <button onclick="testMixed()">Mixed PII Test</button>
            </div>
        </div>

        <script>
        function detectPII() {
            const text = document.getElementById('testText').value;
            if (!text.trim()) {
                alert('Please enter some text to test');
                return;
            }

            fetch('/api/detect-pii', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error detecting PII: ' + error.message);
            });
        }

        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const piiResults = document.getElementById('piiResults');
            const redactedResults = document.getElementById('redactedResults');

            if (data.pii_detected && data.pii_items.length > 0) {
                let html = '<h5>PII Found (' + data.pii_items.length + ' items):</h5>';
                data.pii_items.forEach(item => {
                    html += `<div class="pii-item"><strong>${item.type.toUpperCase()}:</strong> ${item.value} (confidence: ${Math.round(item.confidence * 100)}%)</div>`;
                });
                piiResults.innerHTML = html;
                
                redactedResults.innerHTML = '<h5>Redacted Version:</h5><div class="redacted">' + data.redacted_message + '</div>';
            } else {
                piiResults.innerHTML = '<div class="no-pii">✅ No PII detected in this message</div>';
                redactedResults.innerHTML = '';
            }

            resultsDiv.style.display = 'block';
        }

        function clearResults() {
            document.getElementById('testText').value = '';
            document.getElementById('results').style.display = 'none';
        }

        function testEmail() {
            document.getElementById('testText').value = 'Contact me at john.doe@gmail.com or alice@company.org';
            detectPII();
        }

        function testPhone() {
            document.getElementById('testText').value = 'Call me at 9876543210 or +91 8765432109';
            detectPII();
        }

        function testAadhar() {
            document.getElementById('testText').value = 'My Aadhar number is 1234 5678 9012';
            detectPII();
        }

        function testMixed() {
            document.getElementById('testText').value = 'Hi, my email is test@example.com, phone is 9876543210, and Aadhar is 1234 5678 9012. My PAN is ABCDE1234F.';
            detectPII();
        }
        </script>
    </body>
    </html>
    '''

@app.route('/api/detect-pii', methods=['POST'])
def detect_pii_api():
    """API endpoint for PII detection"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Detect PII in the message
        pii_items = pii_detector.detect_pii(message)
        
        # Generate redacted version if PII found
        redacted_message = pii_detector.redact_pii(message, pii_items) if pii_items else message
        
        return jsonify({
            'pii_detected': len(pii_items) > 0,
            'pii_items': pii_items,
            'original_message': message,
            'redacted_message': redacted_message,
            'detection_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting PII Detection Test Server...")
    print("Visit http://localhost:5000 to test PII detection")
    app.run(host='0.0.0.0', port=5000, debug=True)