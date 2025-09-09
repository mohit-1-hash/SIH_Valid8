"""
Verification Engine - Main certificate verification logic
Orchestrates all verification steps and stores results in database
"""

import os
import hashlib
import json
from datetime import datetime
from app.models.database_models import db, Certificate, Institution
from app.utils.mock_services import (
    MockOCRService, 
    MockWatermarkDetector, 
    MockSignatureVerifier,
    MockTemplateVerifier,
    MockInstitutionAPI
)

class VerificationEngine:
    """Main certificate verification engine"""

    def __init__(self):
        self.ocr_service = MockOCRService()
        self.watermark_detector = MockWatermarkDetector()
        self.signature_verifier = MockSignatureVerifier()
        self.template_verifier = MockTemplateVerifier()
        self.institution_api = MockInstitutionAPI()

    def verify_certificate(self, file_path, verification_link=None, client_info=None):
        """
        Main verification process - 8 steps as specified
        Returns comprehensive verification result
        """

        result = {
            'status': 'unknown',
            'certificate_data': {},
            'verification_steps': [],
            'flags': [],
            'verification_link_used': bool(verification_link),
            'processing_time': 0,
            'timestamp': datetime.now().isoformat()
        }

        start_time = datetime.now()

        try:
            # Step 1: Watermark Verification
            watermark_result = self.verify_watermark(file_path)
            result['verification_steps'].append(self.format_step_result(1, "Watermark Detection", watermark_result))

            # Step 2: Blockchain/Link Verification (if provided)
            if verification_link:
                link_result = self.verify_blockchain_link(verification_link)
                result['verification_steps'].append(self.format_step_result(2, "Blockchain Link Verification", link_result))
                if link_result['verified']:
                    result['status'] = 'verified'
                    result['certificate_data'] = link_result.get('certificate_data', {})
                    end_time = datetime.now()
                    result['processing_time'] = (end_time - start_time).total_seconds()
                    return result
            else:
                result['verification_steps'].append("2. Blockchain Link Verification: ⏭️ Skipped (no link provided)")

            # Step 3: OCR Text Extraction
            ocr_result = self.extract_text_with_ocr(file_path)
            result['verification_steps'].append(self.format_step_result(3, "OCR Text Extraction", ocr_result))

            if ocr_result['success']:
                result['certificate_data'] = ocr_result['extracted_data']
            else:
                result['flags'].append('OCR_EXTRACTION_FAILED')
                result['status'] = 'flag'
                end_time = datetime.now()
                result['processing_time'] = (end_time - start_time).total_seconds()
                return result

            # Step 4: Template Matching
            template_result = self.verify_template_match(result['certificate_data'])
            result['verification_steps'].append(self.format_step_result(4, "Template Matching", template_result))

            if not template_result['template_match']:
                result['flags'].append('TEMPLATE_MISMATCH')

            # Step 5: Digital Signature Verification
            signature_result = self.verify_digital_signature(file_path)
            result['verification_steps'].append(self.format_step_result(5, "Digital Signature Check", signature_result))

            if signature_result['has_signature'] and not signature_result.get('signature_valid', False):
                result['flags'].append('SIGNATURE_INVALID')

            # Step 6: Internal Database Check
            db_result = self.check_internal_database(result['certificate_data'])
            result['verification_steps'].append(self.format_step_result(6, "Internal Database Check", db_result))

            if db_result['found_in_database']:
                result['status'] = 'verified'
                result['certificate_data'].update(db_result['certificate_data'])
                end_time = datetime.now()
                result['processing_time'] = (end_time - start_time).total_seconds()
                return result

            # Step 7: Institution API Verification  
            api_result = self.verify_with_institution_api(result['certificate_data'])
            result['verification_steps'].append(self.format_step_result(7, "Institution API Verification", api_result))

            if api_result['verified']:
                result['status'] = 'verified'
                end_time = datetime.now()
                result['processing_time'] = (end_time - start_time).total_seconds()
                return result

            # Step 8: Manual Verification Required
            manual_info = self.get_manual_verification_info(result['certificate_data'])
            result['verification_steps'].append(self.format_step_result(8, "Manual Verification Required", manual_info))
            result['contact_info'] = manual_info['contact_info']
            result['status'] = 'manual_verification'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['flags'].append('PROCESSING_ERROR')

        end_time = datetime.now()
        result['processing_time'] = (end_time - start_time).total_seconds()

        # Final status determination
        if result['flags'] and result['status'] != 'verified':
            result['status'] = 'flag'

        return result

    def verify_watermark(self, file_path):
        """Step 1: Verify watermark presence and authenticity"""
        try:
            watermark_result = self.watermark_detector.detect_watermark(file_path)

            if watermark_result['has_watermark']:
                return {
                    'passed': True,
                    'message': f"Watermark detected: {watermark_result['watermark_type']}",
                    'confidence': watermark_result['confidence'],
                    'details': watermark_result
                }
            else:
                return {
                    'passed': False,
                    'message': "No watermark detected",
                    'confidence': watermark_result['confidence'],
                    'details': watermark_result
                }
        except Exception as e:
            return {
                'passed': False,
                'message': f"Watermark detection failed: {str(e)}",
                'error': str(e)
            }

    def verify_blockchain_link(self, verification_link):
        """Step 2: Verify certificate through blockchain/verification link"""
        try:
            # Extract hash from verification link if present
            if '/verify/' in verification_link:
                cert_hash = verification_link.split('/verify/')[-1]
                certificate = Certificate.query.filter_by(certificate_hash=cert_hash).first()

                if certificate:
                    return {
                        'verified': True,
                        'message': "Certificate verified via blockchain link",
                        'certificate_data': certificate.to_dict(),
                        'method': 'blockchain_link'
                    }

            return {
                'verified': False,
                'message': "Invalid verification link or certificate not found",
                'method': 'blockchain_link'
            }
        except Exception as e:
            return {
                'verified': False,
                'message': f"Blockchain verification failed: {str(e)}",
                'error': str(e)
            }

    def extract_text_with_ocr(self, file_path):
        """Step 3: Extract text using OCR"""
        try:
            return self.ocr_service.extract_text_from_image(file_path)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"OCR extraction failed: {str(e)}"
            }

    def verify_template_match(self, certificate_data):
        """Step 4: Verify certificate matches institution template"""
        try:
            institution_name = certificate_data.get('institution_name', '')
            return self.template_verifier.verify_template(institution_name, certificate_data)
        except Exception as e:
            return {
                'template_match': False,
                'error': str(e),
                'message': f"Template verification failed: {str(e)}"
            }

    def verify_digital_signature(self, file_path):
        """Step 5: Verify digital signature"""
        try:
            return self.signature_verifier.verify_digital_signature(file_path)
        except Exception as e:
            return {
                'has_signature': False,
                'error': str(e),
                'message': f"Signature verification failed: {str(e)}"
            }

    def check_internal_database(self, certificate_data):
        """Step 6: Check internal database for certificate"""
        try:
            student_name = certificate_data.get('student_name', '')
            institution_name = certificate_data.get('institution_name', '')
            course_name = certificate_data.get('course_name', '')

            # Search for matching certificate in database
            certificate = Certificate.query.filter(
                Certificate.student_name.ilike(f'%{student_name}%'),
                Certificate.institution_name.ilike(f'%{institution_name}%'),
                Certificate.course_name.ilike(f'%{course_name}%')
            ).first()

            if certificate:
                return {
                    'found_in_database': True,
                    'message': "Certificate found in internal database",
                    'certificate_data': certificate.to_dict(),
                    'match_confidence': 0.95
                }
            else:
                return {
                    'found_in_database': False,
                    'message': "Certificate not found in internal database",
                    'match_confidence': 0.0
                }
        except Exception as e:
            return {
                'found_in_database': False,
                'error': str(e),
                'message': f"Database check failed: {str(e)}"
            }

    def verify_with_institution_api(self, certificate_data):
        """Step 7: Verify with institution's API"""
        try:
            institution_name = certificate_data.get('institution_name', '')
            student_name = certificate_data.get('student_name', '')
            course_name = certificate_data.get('course_name', '')

            # Get institution code from database
            institution = Institution.query.filter(
                Institution.name.ilike(f'%{institution_name}%')
            ).first()

            if not institution:
                return {
                    'verified': False,
                    'message': "Institution not found in verified institutions list",
                    'error': 'INSTITUTION_NOT_FOUND'
                }

            # Call mock institution API
            api_result = self.institution_api.verify_certificate(
                institution.code, student_name, course_name
            )

            return api_result
        except Exception as e:
            return {
                'verified': False,
                'error': str(e),
                'message': f"Institution API verification failed: {str(e)}"
            }

    def get_manual_verification_info(self, certificate_data):
        """Step 8: Get manual verification contact information"""
        try:
            institution_name = certificate_data.get('institution_name', '')

            # Get institution from database
            institution = Institution.query.filter(
                Institution.name.ilike(f'%{institution_name}%')
            ).first()

            if institution:
                institution_code = institution.code
                contact_info = self.institution_api.get_institution_contact(institution_code)
            else:
                contact_info = {
                    'phone': 'Contact information not available',
                    'email': 'Please search institution website',
                    'office_hours': 'Standard business hours'
                }

            return {
                'manual_verification_required': True,
                'message': "Please contact institution directly for verification",
                'contact_info': contact_info,
                'institution_name': institution_name
            }
        except Exception as e:
            return {
                'manual_verification_required': True,
                'error': str(e),
                'message': "Manual verification required - contact institution directly",
                'contact_info': {
                    'phone': 'Contact information not available',
                    'email': 'Contact information not available'
                }
            }

    def format_step_result(self, step_number, step_name, result):
        """Format verification step result for display"""
        if isinstance(result, dict):
            if result.get('passed', result.get('verified', result.get('success', False))):
                status = "✓"
                message = result.get('message', f'{step_name} passed')
            else:
                status = "❌" if result.get('error') else "⚠️"
                message = result.get('message', f'{step_name} failed')
        else:
            status = "❌"
            message = f'{step_name} failed'

        return f"{step_number}. {step_name}: {status} {message}"

    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of uploaded file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
