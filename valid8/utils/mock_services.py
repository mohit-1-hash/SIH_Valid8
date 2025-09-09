"""
Mock Services - Simulates external API calls for prototype
"""

import random
import time
from datetime import datetime
import json

class MockDigilockerAPI:
    """Mock DigiLocker API for institution verification"""

    def __init__(self):
        # Pre-defined valid institution codes for testing
        self.valid_institutions = {
            'TECH_UNIV_001': {
                'name': 'Tech University',
                'status': 'active',
                'verification_date': '2024-01-15',
                'accreditation': 'UGC Approved'
            },
            'BIZ_COLLEGE_002': {
                'name': 'Business College',
                'status': 'active', 
                'verification_date': '2024-02-10',
                'accreditation': 'AICTE Approved'
            },
            'MED_SCHOOL_003': {
                'name': 'Medical School',
                'status': 'active',
                'verification_date': '2024-03-05',
                'accreditation': 'MCI Approved'
            },
            'TEST_INST_999': {
                'name': 'Test Institution',
                'status': 'active',
                'verification_date': '2024-08-01',
                'accreditation': 'Test Approved'
            }
        }

    def verify_institution(self, institution_code):
        """Mock institution verification via DigiLocker"""

        # Simulate API delay
        time.sleep(random.uniform(0.5, 2.0))

        if institution_code in self.valid_institutions:
            institution_data = self.valid_institutions[institution_code]
            return {
                'verified': True,
                'institution_code': institution_code,
                'institution_name': institution_data['name'],
                'status': institution_data['status'],
                'verification_date': institution_data['verification_date'],
                'accreditation': institution_data['accreditation'],
                'api_response_time': datetime.now().isoformat()
            }
        else:
            return {
                'verified': False,
                'error': 'Institution not found in DigiLocker registry',
                'error_code': 'INSTITUTION_NOT_FOUND',
                'api_response_time': datetime.now().isoformat()
            }

class MockInstitutionAPI:
    """Mock Institution API for external certificate verification"""

    def __init__(self):
        # Pre-defined valid certificates for testing
        self.valid_certificates = {
            'TECH_UNIV_001': [
                {
                    'student_name': 'John Doe',
                    'course': 'Bachelor of Computer Science',
                    'issue_date': '2024-05-15',
                    'status': 'verified'
                },
                {
                    'student_name': 'Alice Johnson',
                    'course': 'Master of Computer Science',
                    'issue_date': '2024-06-20',
                    'status': 'verified'
                }
            ],
            'BIZ_COLLEGE_002': [
                {
                    'student_name': 'Jane Smith',
                    'course': 'Master of Business Administration',
                    'issue_date': '2024-06-10',
                    'status': 'verified'
                },
                {
                    'student_name': 'Bob Wilson',
                    'course': 'Bachelor of Business',
                    'issue_date': '2024-05-25',
                    'status': 'verified'
                }
            ],
            'MED_SCHOOL_003': [
                {
                    'student_name': 'Alice Johnson',
                    'course': 'Doctor of Medicine',
                    'issue_date': '2024-07-01',
                    'status': 'verified'
                }
            ]
        }

    def verify_certificate(self, institution_code, student_name, course_name):
        """Mock certificate verification via institution API"""

        # Simulate API delay
        time.sleep(random.uniform(1.0, 3.0))

        if institution_code not in self.valid_certificates:
            return {
                'verified': False,
                'error': 'Institution API not available',
                'error_code': 'API_NOT_AVAILABLE'
            }

        # Check if certificate exists
        certificates = self.valid_certificates[institution_code]
        for cert in certificates:
            if (cert['student_name'].lower() == student_name.lower() and 
                cert['course'].lower() in course_name.lower()):
                return {
                    'verified': True,
                    'certificate_data': cert,
                    'verification_method': 'institution_api',
                    'api_response_time': datetime.now().isoformat()
                }

        return {
            'verified': False,
            'error': 'Certificate not found in institution database',
            'error_code': 'CERTIFICATE_NOT_FOUND',
            'api_response_time': datetime.now().isoformat()
        }

    def get_institution_contact(self, institution_code):
        """Get institution contact information for manual verification"""

        contact_info = {
            'TECH_UNIV_001': {
                'phone': '+91-9876543210',
                'email': 'verification@techuniv.edu',
                'office_hours': '9 AM - 5 PM, Monday to Friday'
            },
            'BIZ_COLLEGE_002': {
                'phone': '+91-8765432109',
                'email': 'registrar@bizcollege.edu',
                'office_hours': '10 AM - 4 PM, Monday to Saturday'
            },
            'MED_SCHOOL_003': {
                'phone': '+91-7654321098',
                'email': 'verification@medschool.edu',
                'office_hours': '9 AM - 3 PM, Monday to Friday'
            }
        }

        return contact_info.get(institution_code, {
            'phone': 'Contact information not available',
            'email': 'Contact information not available',
            'office_hours': 'Please contact institution directly'
        })

class MockOCRService:
    """Mock OCR service for text extraction from certificates"""

    def extract_text_from_image(self, file_path):
        """Mock OCR text extraction"""

        # Simulate OCR processing delay
        time.sleep(random.uniform(2.0, 4.0))

        # Generate mock extracted data based on filename or random
        mock_extractions = [
            {
                'student_name': 'John Doe',
                'institution_name': 'Tech University',
                'course_name': 'Bachelor of Computer Science', 
                'year': '2024',
                'grade': 'A',
                'certificate_type': 'degree',
                'confidence': 0.92
            },
            {
                'student_name': 'Jane Smith',
                'institution_name': 'Business College',
                'course_name': 'Master of Business Administration',
                'year': '2024',
                'grade': 'B+',
                'certificate_type': 'degree',
                'confidence': 0.88
            },
            {
                'student_name': 'Alice Johnson',
                'institution_name': 'Medical School',
                'course_name': 'Doctor of Medicine',
                'year': '2024',
                'grade': 'A-',
                'certificate_type': 'degree',
                'confidence': 0.95
            }
        ]

        # Return random extraction or based on filename
        selected_extraction = random.choice(mock_extractions)

        return {
            'success': True,
            'extracted_data': selected_extraction,
            'confidence': selected_extraction['confidence'],
            'processing_time': random.uniform(2.0, 4.0)
        }

class MockWatermarkDetector:
    """Mock watermark detection service"""

    def detect_watermark(self, file_path):
        """Mock watermark detection"""

        # Simulate processing delay
        time.sleep(random.uniform(1.0, 2.0))

        # Random watermark detection result
        has_watermark = random.choice([True, True, True, False])  # 75% chance of having watermark

        if has_watermark:
            return {
                'has_watermark': True,
                'watermark_type': random.choice(['digital', 'text', 'logo']),
                'confidence': random.uniform(0.7, 0.95),
                'location': f'x:{random.randint(100, 500)}, y:{random.randint(100, 300)}'
            }
        else:
            return {
                'has_watermark': False,
                'confidence': random.uniform(0.1, 0.3),
                'reason': 'No watermark pattern detected'
            }

class MockSignatureVerifier:
    """Mock digital signature verification"""

    def verify_digital_signature(self, file_path):
        """Mock digital signature verification"""

        # Simulate processing delay
        time.sleep(random.uniform(1.5, 3.0))

        # Check if PDF (assume only PDFs can have digital signatures)
        if file_path.lower().endswith('.pdf'):
            has_signature = random.choice([True, False, False])  # 33% chance

            if has_signature:
                return {
                    'has_signature': True,
                    'signature_valid': random.choice([True, True, False]),  # 67% valid if present
                    'signer': random.choice(['Tech University', 'Business College', 'Medical School']),
                    'signature_date': '2024-08-15T10:30:00Z',
                    'certificate_valid': True
                }
            else:
                return {
                    'has_signature': False,
                    'reason': 'No digital signature found in PDF'
                }
        else:
            return {
                'has_signature': False,
                'reason': 'File type does not support digital signatures'
            }

class MockTemplateVerifier:
    """Mock template verification against institution templates"""

    def __init__(self):
        # Mock institution templates
        self.institution_templates = {
            'Tech University': {
                'template_hash': 'abc123def456',
                'required_fields': ['student_name', 'course_name', 'issue_date', 'grade'],
                'layout_signature': 'TU_2024_TEMPLATE'
            },
            'Business College': {
                'template_hash': 'xyz789uvw012',
                'required_fields': ['student_name', 'course_name', 'issue_date'],
                'layout_signature': 'BC_2024_TEMPLATE'
            },
            'Medical School': {
                'template_hash': 'mno345pqr678',
                'required_fields': ['student_name', 'course_name', 'issue_date', 'grade'],
                'layout_signature': 'MS_2024_TEMPLATE'
            }
        }

    def verify_template(self, institution_name, extracted_data):
        """Mock template verification"""

        # Simulate processing delay
        time.sleep(random.uniform(1.0, 2.0))

        if institution_name not in self.institution_templates:
            return {
                'template_match': False,
                'error': 'No template found for institution',
                'confidence': 0.0
            }

        template = self.institution_templates[institution_name]

        # Check if required fields are present
        missing_fields = []
        for field in template['required_fields']:
            if field not in extracted_data or not extracted_data[field]:
                missing_fields.append(field)

        if missing_fields:
            return {
                'template_match': False,
                'missing_fields': missing_fields,
                'confidence': random.uniform(0.2, 0.4)
            }
        else:
            return {
                'template_match': True,
                'template_hash': template['template_hash'],
                'layout_signature': template['layout_signature'],
                'confidence': random.uniform(0.85, 0.98)
            }
