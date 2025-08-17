#!/usr/bin/env python3
"""
Unlabeled PII Training Dataset for Unsupervised Learning
Contains real-world text patterns for TF-IDF and clustering training
"""

# Unlabeled dataset with various text patterns containing potential PII
PII_TRAINING_CORPUS = [
    # Email patterns in natural text
    "Please contact me at my email address for further details",
    "You can reach out via email whenever convenient",
    "Send the documents to my work email when ready",
    "My personal email is checked daily",
    "Business inquiries should go to the company email",
    
    # Phone number contexts
    "Call me on my mobile number during business hours",
    "My contact number is available on the website",
    "Please share your phone number for verification",
    "I can be reached at my home phone after 6 PM",
    "Emergency contact number should be provided",
    
    # Name and identity patterns
    "My full name appears on all official documents",
    "Please update the name on my account profile",
    "The person named in the contract is responsible",
    "First name and last name must match exactly",
    "Legal name change requires proper documentation",
    
    # Address and location contexts
    "My home address has changed recently",
    "Please ship to the billing address provided",
    "Office address is listed in the directory",
    "Current residential address needs verification",
    "Mailing address should be kept confidential",
    
    # Financial information patterns
    "Bank account details are required for transfer",
    "Credit card information must be encrypted",
    "Account number verification is mandatory",
    "Please provide your banking details securely",
    "Financial account access requires authentication",
    
    # Date of birth and age contexts
    "Date of birth verification is required",
    "Please confirm your birth date for security",
    "Age verification helps protect privacy",
    "Birth year determines eligibility criteria",
    "Date of birth matches government records",
    
    # Government ID patterns
    "Social security number is kept confidential",
    "Passport number verification completed successfully",
    "Driver license information updated recently",
    "Government ID number required for registration",
    "Official identification documents submitted",
    
    # General privacy and personal info
    "Personal information should remain private",
    "Sensitive data requires special handling",
    "Confidential details shared securely",
    "Private information protected by policy",
    "Personal data processing follows regulations",
    
    # Professional and business contexts
    "Employee identification number assigned",
    "Customer account information updated",
    "Business registration details verified",
    "Professional contact information current",
    "Corporate identity documents reviewed",
    
    # Medical and health contexts
    "Medical record number confidential",
    "Health information privacy protected",
    "Patient identification verified securely",
    "Healthcare data access restricted",
    "Medical history kept confidential",
    
    # Educational contexts
    "Student identification number required",
    "Academic records remain confidential",
    "Educational background verification",
    "School enrollment information private",
    "University transcript access limited",
    
    # Technology and digital contexts
    "Username and password combination",
    "Digital identity verification required",
    "Online account security enhanced",
    "User profile information updated",
    "Digital signature authentication",
    
    # Generic conversational patterns
    "I need to share some personal details",
    "Let me give you my contact information",
    "Here are my current details for your records",
    "Please keep this information confidential",
    "My details have been updated recently",
    
    # Mixed context sentences
    "Contact information including email and phone",
    "Personal details such as name and address",
    "Identity verification requires multiple documents",
    "Account information including numbers and dates",
    "Registration requires personal and financial data",
    
    # Industry-specific contexts
    "Legal case requires identity disclosure",
    "Medical appointment needs contact details",
    "Banking transaction requires verification",
    "Insurance claim needs personal information",
    "Employment application requires background check",
    
    # Security and privacy contexts
    "Data protection measures implemented",
    "Privacy policy covers personal information",
    "Security protocol protects sensitive data",
    "Confidentiality agreement signed",
    "Information security standards followed",
    
    # Communication patterns
    "Please call me at the number provided",
    "Email response expected within business hours",
    "Text message confirmation will be sent",
    "Written correspondence should use formal address",
    "Digital communication preferred for quick response",
    
    # Verification and validation contexts
    "Identity confirmation process completed",
    "Information accuracy verified independently",
    "Details cross-referenced with official records",
    "Validation requires additional documentation",
    "Confirmation sent to registered contact method",
    
    # Additional natural language patterns
    "My information is stored securely in the system",
    "Please update your profile with current details",
    "Account holder information must be accurate",
    "Registration details expire after one year",
    "Contact preferences can be modified anytime",
    
    # Location and geography contexts
    "Shipping address differs from billing location",
    "Geographic location affects service availability",
    "Regional office handles local inquiries",
    "Location services require permission",
    "Address verification prevents fraud",
    
    # Time and scheduling contexts
    "Appointment scheduled for specific date",
    "Birthday celebration planned for weekend",
    "Anniversary date remembered annually",
    "Meeting scheduled during business hours",
    "Deadline approaches for submission",
    
    # Relationship and family contexts
    "Family member contact information needed",
    "Emergency contact person designated",
    "Next of kin notification required",
    "Spouse information included in application",
    "Dependent details affect coverage",
]

# PII-related keywords for context learning
PII_KEYWORD_CONTEXTS = [
    # Direct PII indicators
    "email", "phone", "address", "name", "birth", "social", "passport",
    "license", "account", "number", "contact", "identity", "personal",
    
    # Action verbs related to PII
    "provide", "share", "give", "send", "update", "verify", "confirm",
    "register", "submit", "enter", "include", "attach", "upload",
    
    # Security and privacy terms
    "confidential", "secure", "private", "protected", "encrypted",
    "verified", "authenticated", "authorized", "restricted", "limited",
    
    # Document and record types
    "document", "record", "file", "form", "application", "profile",
    "account", "registration", "enrollment", "membership",
    
    # Communication channels
    "email", "phone", "text", "mail", "message", "call", "contact",
    "communication", "correspondence", "notification",
    
    # Organizational contexts
    "company", "organization", "institution", "department", "office",
    "business", "corporate", "professional", "official", "government",
]

# Sensitive information patterns (for clustering training)
SENSITIVE_PATTERNS = [
    # Financial patterns
    "banking information", "credit card details", "account balance",
    "financial history", "payment information", "billing details",
    
    # Medical patterns
    "medical history", "health records", "diagnosis information",
    "treatment details", "medication list", "doctor visits",
    
    # Legal patterns
    "legal documents", "court records", "case information",
    "lawyer contact", "legal proceedings", "litigation details",
    
    # Employment patterns
    "employment history", "salary information", "job application",
    "resume details", "work experience", "employer contact",
    
    # Educational patterns
    "academic records", "transcript information", "school details",
    "education history", "degree information", "certification details",
]

def get_training_corpus():
    """Get the complete training corpus for unsupervised learning"""
    return PII_TRAINING_CORPUS + [f"Context involving {keyword}" for keyword in PII_KEYWORD_CONTEXTS]

def get_sensitive_patterns():
    """Get sensitive information patterns for clustering"""
    return SENSITIVE_PATTERNS

def get_pii_keywords():
    """Get PII-related keywords for context analysis"""
    return PII_KEYWORD_CONTEXTS