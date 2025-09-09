"""
Database Models for Certificate Verification System
Stores certificates, hashes, and verification data in regular database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for institution and admin authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'institution' or 'admin'
    institution_name = db.Column(db.String(200))
    institution_code = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    certificates = db.relationship('Certificate', backref='institution_user', lazy=True)

class Institution(db.Model):
    """Institution model for storing verified institutions"""
    __tablename__ = 'institutions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    verification_source = db.Column(db.String(50))  # 'digilocker', 'manual', etc.
    api_endpoint = db.Column(db.String(500))  # For mock API calls
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    """Certificate model for storing certificate data and hashes"""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    institution_name = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    grade = db.Column(db.String(20))
    certificate_type = db.Column(db.String(50), default='degree')

    # Hash storage (instead of blockchain)
    certificate_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    file_hash = db.Column(db.String(64))  # Hash of uploaded file
    data_hash = db.Column(db.String(64))  # Hash of certificate data

    # File information
    file_path = db.Column(db.String(500))
    file_type = db.Column(db.String(10))

    # Verification status
    is_verified = db.Column(db.Boolean, default=True)
    verification_method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def generate_certificate_hash(self):
        """Generate SHA-256 hash of certificate data"""
        data_string = f"{self.student_name}{self.course_name}{self.institution_name}{self.issue_date}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    def to_dict(self):
        """Convert certificate to dictionary"""
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'student_name': self.student_name,
            'course_name': self.course_name,
            'institution_name': self.institution_name,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'grade': self.grade,
            'certificate_type': self.certificate_type,
            'certificate_hash': self.certificate_hash,
            'is_verified': self.is_verified
        }

class VerificationAttempt(db.Model):
    """Log of certificate verification attempts"""
    __tablename__ = 'verification_attempts'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    file_hash = db.Column(db.String(64))
    verification_status = db.Column(db.String(50))  # 'verified', 'flag', 'manual'
    verification_steps = db.Column(db.JSON)  # Store verification process as JSON
    extracted_data = db.Column(db.JSON)  # OCR extracted data
    flags_detected = db.Column(db.JSON)  # Any flags/issues found
    institution_matched = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Flag(db.Model):
    """Flags for suspicious verification attempts"""
    __tablename__ = 'flags'

    id = db.Column(db.Integer, primary_key=True)
    flag_type = db.Column(db.String(100), nullable=False)
    institution_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    verification_attempt_id = db.Column(db.Integer, db.ForeignKey('verification_attempts.id'))
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MockAPIResponse(db.Model):
    """Mock API responses for testing external verification"""
    __tablename__ = 'mock_api_responses'

    id = db.Column(db.Integer, primary_key=True)
    institution_code = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(200))
    course_name = db.Column(db.String(200))
    response_data = db.Column(db.JSON)  # Mock response data
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_sample_data():
    """Create sample data for testing"""

    # Check if data already exists
    if User.query.first():
        return

    from werkzeug.security import generate_password_hash

    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@certverify.com',
        password_hash=generate_password_hash('admin123'),
        user_type='admin',
        institution_name='System Admin'
    )
    db.session.add(admin_user)

    # Create sample institutions
    institutions_data = [
        {
            'name': 'Tech University',
            'code': 'TECH_UNIV_001',
            'email': 'registrar@techuniv.edu',
            'phone': '+91-9876543210',
            'is_verified': True,
            'verification_source': 'digilocker'
        },
        {
            'name': 'Business College', 
            'code': 'BIZ_COLLEGE_002',
            'email': 'admin@bizcollege.edu',
            'phone': '+91-8765432109',
            'is_verified': True,
            'verification_source': 'digilocker'
        },
        {
            'name': 'Medical School',
            'code': 'MED_SCHOOL_003', 
            'email': 'verification@medschool.edu',
            'phone': '+91-7654321098',
            'is_verified': True,
            'verification_source': 'manual'
        }
    ]

    for inst_data in institutions_data:
        institution = Institution(**inst_data)
        db.session.add(institution)

        # Create institution user
        inst_user = User(
            username=inst_data['code'].lower(),
            email=inst_data['email'],
            password_hash=generate_password_hash('password123'),
            user_type='institution',
            institution_name=inst_data['name'],
            institution_code=inst_data['code']
        )
        db.session.add(inst_user)

    # Create sample certificates
    sample_certificates = [
        {
            'certificate_id': 'CERT-TECH-001-2024',
            'student_name': 'John Doe',
            'course_name': 'Bachelor of Computer Science',
            'institution_name': 'Tech University',
            'issue_date': datetime(2024, 5, 15).date(),
            'grade': 'A',
            'certificate_type': 'degree'
        },
        {
            'certificate_id': 'CERT-BIZ-002-2024',
            'student_name': 'Jane Smith',
            'course_name': 'Master of Business Administration', 
            'institution_name': 'Business College',
            'issue_date': datetime(2024, 6, 20).date(),
            'grade': 'B+',
            'certificate_type': 'degree'
        },
        {
            'certificate_id': 'CERT-MED-003-2024',
            'student_name': 'Alice Johnson',
            'course_name': 'Doctor of Medicine',
            'institution_name': 'Medical School',
            'issue_date': datetime(2024, 7, 10).date(),
            'grade': 'A-',
            'certificate_type': 'degree'
        }
    ]

    for cert_data in sample_certificates:
        # Find institution user
        inst_user = User.query.filter_by(institution_name=cert_data['institution_name']).first()
        if inst_user:
            certificate = Certificate(
                institution_id=inst_user.id,
                **cert_data
            )
            certificate.certificate_hash = certificate.generate_certificate_hash()
            certificate.data_hash = hashlib.sha256(json.dumps(cert_data, default=str).encode()).hexdigest()
            db.session.add(certificate)

    # Create mock API responses
    mock_responses = [
        {
            'institution_code': 'TECH_UNIV_001',
            'student_name': 'John Doe',
            'course_name': 'Bachelor of Computer Science',
            'response_data': {'verified': True, 'status': 'active'},
            'is_verified': True
        },
        {
            'institution_code': 'BIZ_COLLEGE_002',
            'student_name': 'Jane Smith', 
            'course_name': 'Master of Business Administration',
            'response_data': {'verified': True, 'status': 'graduated'},
            'is_verified': True
        }
    ]

    for mock_data in mock_responses:
        mock_response = MockAPIResponse(**mock_data)
        db.session.add(mock_response)

    try:
        db.session.commit()
        print("✓ Sample data created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")
