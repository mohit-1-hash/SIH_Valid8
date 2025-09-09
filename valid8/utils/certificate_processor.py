"""
Certificate Processor - Handles file uploads, bulk processing, and certificate storage
"""

import os
import csv
import uuid
import hashlib
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from app.models.database_models import db, Certificate

class CertificateProcessor:
    """Processes certificate uploads and bulk operations"""

    def __init__(self):
        self.allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'csv'}
        self.upload_folder = 'app/static/uploads'

    def process_single_upload(self, request, user):
        """Process single certificate upload from institution"""
        try:
            # Validate form data
            required_fields = ['student_name', 'course_name', 'issue_date', 'certificate_type']
            form_data = {}

            for field in required_fields:
                value = request.form.get(field)
                if not value:
                    return {'success': False, 'error': f'Missing required field: {field}'}
                form_data[field] = value

            # Handle file upload
            if 'certificate_file' not in request.files:
                return {'success': False, 'error': 'No certificate file uploaded'}

            file = request.files['certificate_file']
            if file.filename == '' or not self.allowed_file(file.filename):
                return {'success': False, 'error': 'Invalid file type'}

            # Save uploaded file
            filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)

            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)

            # Create certificate record
            certificate_id = self.generate_certificate_id(user.institution_code)

            certificate = Certificate(
                certificate_id=certificate_id,
                student_name=form_data['student_name'],
                course_name=form_data['course_name'],
                institution_id=user.id,
                institution_name=user.institution_name,
                issue_date=datetime.strptime(form_data['issue_date'], '%Y-%m-%d').date(),
                certificate_type=form_data['certificate_type'],
                grade=request.form.get('grade', ''),
                file_path=file_path,
                file_type=file.filename.split('.')[-1].lower(),
                file_hash=file_hash,
                is_verified=True,
                verification_method='institution_upload'
            )

            # Generate certificate hash
            certificate.certificate_hash = certificate.generate_certificate_hash()

            # Generate data hash
            data_dict = {
                'student_name': certificate.student_name,
                'course_name': certificate.course_name,
                'institution_name': certificate.institution_name,
                'issue_date': certificate.issue_date.isoformat(),
                'certificate_type': certificate.certificate_type
            }
            certificate.data_hash = hashlib.sha256(
                json.dumps(data_dict, sort_keys=True).encode()
            ).hexdigest()

            # Save to database
            db.session.add(certificate)
            db.session.commit()

            return {
                'success': True,
                'count': 1,
                'certificate_id': certificate_id,
                'certificate_hash': certificate.certificate_hash
            }

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    def process_bulk_upload(self, request, user):
        """Process bulk certificate upload via CSV"""
        try:
            if 'bulk_file' not in request.files:
                return {'success': False, 'error': 'No CSV file uploaded'}

            file = request.files['bulk_file']
            if file.filename == '' or not file.filename.lower().endswith('.csv'):
                return {'success': False, 'error': 'Please upload a CSV file'}

            # Save uploaded CSV file temporarily
            csv_filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
            csv_file_path = os.path.join(self.upload_folder, csv_filename)
            file.save(csv_file_path)

            # Process CSV file
            certificates_created = []
            errors = []

            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate CSV headers
                required_columns = ['student_name', 'course_name', 'issue_date', 'certificate_type']
                if not all(col in reader.fieldnames for col in required_columns):
                    return {
                        'success': False, 
                        'error': f'CSV missing required columns: {required_columns}'
                    }

                row_count = 0
                for row in reader:
                    row_count += 1

                    if row_count > 1000:  # Limit bulk upload size
                        errors.append(f'Row {row_count}: Bulk upload limit exceeded (1000 rows max)')
                        break

                    try:
                        # Validate row data
                        if not all(row.get(col, '').strip() for col in required_columns):
                            errors.append(f'Row {row_count}: Missing required data')
                            continue

                        # Create certificate record
                        certificate_id = self.generate_certificate_id(user.institution_code)

                        certificate = Certificate(
                            certificate_id=certificate_id,
                            student_name=row['student_name'].strip(),
                            course_name=row['course_name'].strip(),
                            institution_id=user.id,
                            institution_name=user.institution_name,
                            issue_date=datetime.strptime(row['issue_date'].strip(), '%Y-%m-%d').date(),
                            certificate_type=row['certificate_type'].strip(),
                            grade=row.get('grade', '').strip(),
                            file_type='csv',
                            is_verified=True,
                            verification_method='bulk_upload'
                        )

                        # Generate hashes
                        certificate.certificate_hash = certificate.generate_certificate_hash()

                        data_dict = {
                            'student_name': certificate.student_name,
                            'course_name': certificate.course_name,
                            'institution_name': certificate.institution_name,
                            'issue_date': certificate.issue_date.isoformat(),
                            'certificate_type': certificate.certificate_type
                        }
                        certificate.data_hash = hashlib.sha256(
                            json.dumps(data_dict, sort_keys=True).encode()
                        ).hexdigest()

                        db.session.add(certificate)
                        certificates_created.append(certificate_id)

                    except ValueError as ve:
                        errors.append(f'Row {row_count}: Invalid date format - {str(ve)}')
                    except Exception as e:
                        errors.append(f'Row {row_count}: {str(e)}')

            # Commit all certificates
            db.session.commit()

            # Clean up CSV file
            os.remove(csv_file_path)

            result = {
                'success': True,
                'count': len(certificates_created),
                'certificate_ids': certificates_created
            }

            if errors:
                result['errors'] = errors
                result['error_count'] = len(errors)

            return result

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    def process_batch_verification(self, csv_file):
        """Process batch certificate verification from CSV"""
        try:
            # Save uploaded file temporarily
            csv_filename = secure_filename(str(uuid.uuid4()) + '_batch_verify.csv')
            csv_file_path = os.path.join(self.upload_folder, csv_filename)
            csv_file.save(csv_file_path)

            results = []

            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Expected columns for batch verification
                required_columns = ['student_name', 'institution_name', 'course_name']
                if not all(col in reader.fieldnames for col in required_columns):
                    return {
                        'success': False,
                        'error': f'CSV missing required columns: {required_columns}'
                    }

                row_count = 0
                for row in reader:
                    row_count += 1

                    if row_count > 100:  # Limit batch verification
                        break

                    # Search for certificate in database
                    certificate = Certificate.query.filter(
                        Certificate.student_name.ilike(f'%{row["student_name"].strip()}%'),
                        Certificate.institution_name.ilike(f'%{row["institution_name"].strip()}%'),
                        Certificate.course_name.ilike(f'%{row["course_name"].strip()}%')
                    ).first()

                    result = {
                        'row': row_count,
                        'student_name': row['student_name'].strip(),
                        'institution_name': row['institution_name'].strip(),
                        'course_name': row['course_name'].strip(),
                        'verified': bool(certificate),
                        'certificate_data': certificate.to_dict() if certificate else {}
                    }

                    results.append(result)

            # Clean up CSV file
            os.remove(csv_file_path)

            return {
                'success': True,
                'results': results,
                'total_processed': len(results)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_certificate_id(self, institution_code):
        """Generate unique certificate ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"CERT-{institution_code}-{timestamp}-{random_suffix}"

    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def get_certificate_stats(self, user):
        """Get certificate statistics for institution dashboard"""
        certificates = Certificate.query.filter_by(institution_id=user.id).all()

        stats = {
            'total_certificates': len(certificates),
            'verified_certificates': len([c for c in certificates if c.is_verified]),
            'certificate_types': {},
            'monthly_uploads': {},
            'recent_certificates': []
        }

        # Count by certificate type
        for cert in certificates:
            cert_type = cert.certificate_type
            stats['certificate_types'][cert_type] = stats['certificate_types'].get(cert_type, 0) + 1

        # Count by month
        for cert in certificates:
            month = cert.created_at.strftime('%Y-%m')
            stats['monthly_uploads'][month] = stats['monthly_uploads'].get(month, 0) + 1

        # Recent certificates (last 10)
        stats['recent_certificates'] = sorted(certificates, key=lambda x: x.created_at, reverse=True)[:10]

        return stats

    def export_certificates_csv(self, user):
        """Export institution's certificates to CSV"""
        certificates = Certificate.query.filter_by(institution_id=user.id).all()

        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Certificate ID', 'Student Name', 'Course Name', 
            'Issue Date', 'Grade', 'Certificate Type',
            'Certificate Hash', 'Created At'
        ])

        # Write data
        for cert in certificates:
            writer.writerow([
                cert.certificate_id,
                cert.student_name,
                cert.course_name,
                cert.issue_date.isoformat() if cert.issue_date else '',
                cert.grade or '',
                cert.certificate_type,
                cert.certificate_hash,
                cert.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        output.seek(0)
        return output.getvalue()
