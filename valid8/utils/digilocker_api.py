
import hashlib
import hmac
import time
import json
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

class DigilockerAPI:
    """DigiLocker API integration for institution verification"""

    def __init__(self):
        # These should be loaded from environment variables in production
        self.base_url = "https://api.digitallocker.gov.in"  # Replace with actual URL
        self.client_id = "your_client_id"  # Replace with actual client ID
        self.client_secret = "your_client_secret"  # Replace with actual secret
        self.partner_id = "your_partner_id"  # Replace with actual partner ID

        # Cache for verification results (expires after 24 hours)
        self.verification_cache = {}
        self.cache_timeout = 24 * 60 * 60  # 24 hours in seconds

    def verify_institution(self, institution_code: str) -> Dict:
        """Verify institution with DigiLocker credential registry"""

        # Check cache first
        cache_key = f"institution_{institution_code}"
        if self._is_cached_and_valid(cache_key):
            return self.verification_cache[cache_key]['data']

        try:
            # Generate timestamp and HMAC
            timestamp = int(time.time())
            hmac_string = self._generate_hmac(self.client_secret, self.client_id, timestamp)

            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._get_access_token()}'
            }

            payload = {
                'client_id': self.client_id,
                'ts': timestamp,
                'hmac': hmac_string,
                'institution_code': institution_code
            }

            # Make API request (simulated for now)
            response = self._make_request('POST', '/verify/institution', headers, payload)

            if response.get('success'):
                result = {
                    'verified': True,
                    'institution_name': response.get('institution_name', ''),
                    'registration_number': response.get('registration_number', ''),
                    'status': response.get('status', 'active'),
                    'verification_date': datetime.now().isoformat()
                }
            else:
                result = {
                    'verified': False,
                    'error': response.get('error', 'Verification failed'),
                    'error_code': response.get('error_code', 'UNKNOWN')
                }

            # Cache the result
            self._cache_result(cache_key, result)
            return result

        except Exception as e:
            return {
                'verified': False,
                'error': str(e),
                'error_code': 'API_ERROR'
            }

    def _generate_hmac(self, client_secret: str, client_id: str, timestamp: int) -> str:
        """Generate HMAC for DigiLocker API authentication"""
        # Concatenate without separators as per DigiLocker spec
        message = f"{client_secret}{client_id}{timestamp}"

        # Generate SHA-256 hash (not HMAC as per DigiLocker docs)
        return hashlib.sha256(message.encode()).hexdigest()

    def _get_access_token(self) -> Optional[str]:
        """Get access token for DigiLocker API (implement OAuth flow)"""
        # This is a placeholder - implement actual OAuth flow
        return "dummy_access_token"

    def _make_request(self, method: str, endpoint: str, headers: Dict, data: Dict = None) -> Dict:
        """Make HTTP request to DigiLocker API"""

        # For demo purposes, simulate API responses
        if endpoint == '/verify/institution':
            return self._simulate_institution_verification(data.get('institution_code', ''))

        try:
            url = f"{self.base_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, headers=headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'REQUEST_FAILED'
            }

    def _simulate_institution_verification(self, institution_code: str) -> Dict:
        """Simulate DigiLocker institution verification response"""

        # Predefined valid institution codes for demo
        valid_institutions = {
            'TECH_UNIV_001': {
                'institution_name': 'Tech University',
                'registration_number': 'TU-2020-001',
                'status': 'active',
                'accreditation': 'UGC Approved'
            },
            'BIZ_COLLEGE_002': {
                'institution_name': 'Business College',
                'registration_number': 'BC-2019-002', 
                'status': 'active',
                'accreditation': 'AICTE Approved'
            },
            'MED_SCHOOL_003': {
                'institution_name': 'Medical School',
                'registration_number': 'MS-2018-003',
                'status': 'active',
                'accreditation': 'MCI Approved'
            },
            'DEMO_INST_999': {
                'institution_name': 'Demo Institution',
                'registration_number': 'DI-2024-999',
                'status': 'active',
                'accreditation': 'Demo Approved'
            }
        }

        if institution_code in valid_institutions:
            return {
                'success': True,
                **valid_institutions[institution_code]
            }
        else:
            return {
                'success': False,
                'error': 'Institution not found in registry',
                'error_code': 'INSTITUTION_NOT_FOUND'
            }

    def verify_document(self, document_uri: str, access_token: str) -> Dict:
        """Verify document from DigiLocker"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'uri': document_uri,
                'client_id': self.client_id
            }

            response = self._make_request('POST', '/verify/document', headers, payload)

            return {
                'verified': response.get('success', False),
                'document_info': response.get('document_info', {}),
                'verification_status': response.get('status', 'unknown')
            }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }

    def get_issued_documents(self, institution_code: str, access_token: str) -> Dict:
        """Get list of documents issued by an institution"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'institution_code': institution_code,
                'client_id': self.client_id
            }

            response = self._make_request('GET', '/documents/issued', headers, payload)

            return {
                'success': response.get('success', False),
                'documents': response.get('documents', []),
                'total_count': response.get('total_count', 0)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'documents': []
            }

    def _is_cached_and_valid(self, cache_key: str) -> bool:
        """Check if cached result exists and is still valid"""
        if cache_key not in self.verification_cache:
            return False

        cached_entry = self.verification_cache[cache_key]
        cache_time = cached_entry['timestamp']

        return (time.time() - cache_time) < self.cache_timeout

    def _cache_result(self, cache_key: str, result: Dict):
        """Cache verification result"""
        self.verification_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }

    def clear_cache(self):
        """Clear verification cache"""
        self.verification_cache.clear()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.verification_cache)
        expired_entries = 0

        current_time = time.time()
        for entry in self.verification_cache.values():
            if (current_time - entry['timestamp']) >= self.cache_timeout:
                expired_entries += 1

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries
        }

    def validate_api_credentials(self) -> Dict:
        """Validate API credentials with DigiLocker"""
        try:
            timestamp = int(time.time())
            hmac_string = self._generate_hmac(self.client_secret, self.client_id, timestamp)

            headers = {'Content-Type': 'application/json'}
            payload = {
                'client_id': self.client_id,
                'ts': timestamp,
                'hmac': hmac_string
            }

            response = self._make_request('POST', '/validate/credentials', headers, payload)

            return {
                'valid': response.get('success', False),
                'message': response.get('message', ''),
                'expires_at': response.get('expires_at', '')
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    def get_supported_document_types(self) -> Dict:
        """Get supported document types from DigiLocker"""
        # Static list for demo - in production this would be an API call
        return {
            'education': [
                'degree_certificate',
                'diploma_certificate', 
                'marksheet',
                'transcript',
                'passing_certificate'
            ],
            'identity': [
                'aadhaar',
                'pan_card',
                'driving_license',
                'passport'
            ],
            'professional': [
                'professional_certificate',
                'license',
                'registration_certificate'
            ]
        }
