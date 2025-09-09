
import cv2
import numpy as np
import pytesseract
from PIL import Image
import pdf2image
import re
from typing import Dict, List, Optional, Tuple

class OCRProcessor:
    """Advanced OCR processor for certificate text extraction"""

    def __init__(self):
        # Configure tesseract (adjust path for your system)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

        # OCR configuration for better accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,- '

        # Patterns for extracting specific information
        self.patterns = {
            'student_name': [
                r'(?:Name|Student Name|Full Name)[\s:]+([A-Za-z ]+)',
                r'This is to certify that[\s\n]+([A-Za-z ]+)',
                r'Mr\.?\s+([A-Za-z ]+)|Ms\.?\s+([A-Za-z ]+)'
            ],
            'institution': [
                r'([A-Za-z ]+(?:University|College|Institute|School))',
                r'From[\s:]+([A-Za-z ]+(?:University|College|Institute))',
                r'Issued by[\s:]+([A-Za-z ]+(?:University|College|Institute))'
            ],
            'course': [
                r'(?:Course|Program|Degree|Diploma)[\s:]+([A-Za-z ]+)',
                r'Bachelor of ([A-Za-z ]+)|Master of ([A-Za-z ]+)',
                r'has successfully completed[\s\n]+([A-Za-z ]+)'
            ],
            'year': [
                r'(20\d{2})',
                r'Year[\s:]+([0-9]{4})',
                r'Graduated in[\s:]+([0-9]{4})'
            ],
            'grade': [
                r'(?:Grade|CGPA|Percentage)[\s:]+([A-Z0-9.%]+)',
                r'with[\s]+([A-Z][a-z]+ Class)',
                r'secured[\s]+([0-9.%]+)'
            ]
        }

    def extract_text(self, file_path: str) -> Dict:
        """Extract text from PDF or image file"""
        try:
            # Determine file type and process accordingly
            if file_path.lower().endswith('.pdf'):
                return self._process_pdf(file_path)
            else:
                return self._process_image(file_path)

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extracted_data': {},
                'raw_text': ''
            }

    def _process_pdf(self, pdf_path: str) -> Dict:
        """Process PDF file and extract text"""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)

            all_text = ""
            best_page_text = ""
            best_confidence = 0

            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Process image and extract text
                page_result = self._process_opencv_image(cv_image)

                if page_result['success']:
                    all_text += page_result['raw_text'] + "\n"

                    # Keep track of page with highest confidence
                    if page_result.get('confidence', 0) > best_confidence:
                        best_confidence = page_result.get('confidence', 0)
                        best_page_text = page_result['raw_text']

            # Extract structured data from best page or combined text
            text_to_process = best_page_text if best_page_text else all_text
            extracted_data = self._extract_structured_data(text_to_process)

            return {
                'success': True,
                'raw_text': all_text.strip(),
                'extracted_data': extracted_data,
                'confidence': best_confidence,
                'pages_processed': len(images)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"PDF processing failed: {str(e)}",
                'extracted_data': {},
                'raw_text': ''
            }

    def _process_image(self, image_path: str) -> Dict:
        """Process image file and extract text"""
        try:
            # Read image using OpenCV
            image = cv2.imread(image_path)

            if image is None:
                raise Exception("Could not load image")

            return self._process_opencv_image(image)

        except Exception as e:
            return {
                'success': False,
                'error': f"Image processing failed: {str(e)}",
                'extracted_data': {},
                'raw_text': ''
            }

    def _process_opencv_image(self, image: np.ndarray) -> Dict:
        """Process OpenCV image with preprocessing for better OCR"""
        try:
            # Image preprocessing for better OCR
            processed_image = self._preprocess_image(image)

            # Extract text using Tesseract
            raw_text = pytesseract.image_to_string(processed_image, config=self.ocr_config)

            # Get confidence scores
            confidence_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            avg_confidence = np.mean([int(conf) for conf in confidence_data['conf'] if int(conf) > 0])

            # Extract structured data
            extracted_data = self._extract_structured_data(raw_text)

            return {
                'success': True,
                'raw_text': raw_text.strip(),
                'extracted_data': extracted_data,
                'confidence': avg_confidence
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"OCR processing failed: {str(e)}",
                'extracted_data': {},
                'raw_text': ''
            }

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Resize image if too small (OCR works better on larger images)
        height, width = gray.shape
        if height < 800 or width < 600:
            scale_factor = max(800/height, 600/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations to clean up the image
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Invert if text is white on black background
        if np.mean(cleaned) < 127:
            cleaned = cv2.bitwise_not(cleaned)

        return cleaned

    def _extract_structured_data(self, text: str) -> Dict:
        """Extract structured data from raw text using regex patterns"""
        extracted = {
            'student_name': '',
            'institution': '',
            'course': '',
            'year': '',
            'grade': '',
            'certificate_type': 'unknown'
        }

        # Clean text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s.,()-]', '', text)  # Remove special characters

        # Extract information using patterns
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Get the first non-empty group
                    for group in match.groups():
                        if group and group.strip():
                            extracted[field] = group.strip()
                            break
                    if extracted[field]:  # If we found something, stop looking
                        break

        # Determine certificate type based on content
        extracted['certificate_type'] = self._determine_certificate_type(text)

        # Additional post-processing
        extracted = self._post_process_extracted_data(extracted, text)

        return extracted

    def _determine_certificate_type(self, text: str) -> str:
        """Determine certificate type from text content"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['bachelor', 'b.sc', 'b.tech', 'b.a', 'b.com']):
            return 'bachelor_degree'
        elif any(word in text_lower for word in ['master', 'm.sc', 'm.tech', 'm.a', 'm.com', 'mba']):
            return 'master_degree'
        elif any(word in text_lower for word in ['doctor', 'phd', 'ph.d']):
            return 'doctoral_degree'
        elif any(word in text_lower for word in ['diploma', 'certificate']):
            return 'diploma'
        elif any(word in text_lower for word in ['completion', 'participation']):
            return 'certificate'
        else:
            return 'unknown'

    def _post_process_extracted_data(self, extracted: Dict, full_text: str) -> Dict:
        """Post-process extracted data for better accuracy"""
        # Clean up student name
        if extracted['student_name']:
            # Remove common prefixes and clean up
            name = extracted['student_name']
            name = re.sub(r'^(Mr\.?|Ms\.?|Mrs\.?|Dr\.?)\s*', '', name, flags=re.IGNORECASE)
            name = re.sub(r'\s+', ' ', name).strip()
            extracted['student_name'] = name

        # Clean up institution name
        if extracted['institution']:
            institution = extracted['institution']
            # Capitalize properly
            institution = ' '.join(word.capitalize() for word in institution.split())
            extracted['institution'] = institution

        # Validate year
        if extracted['year']:
            year = extracted['year']
            if len(year) == 4 and year.isdigit():
                year_int = int(year)
                if not (1950 <= year_int <= 2030):  # Reasonable year range
                    extracted['year'] = ''

        # Clean up course name
        if extracted['course']:
            course = extracted['course']
            course = ' '.join(word.capitalize() for word in course.split())
            extracted['course'] = course

        return extracted

    def get_text_regions(self, file_path: str) -> List[Dict]:
        """Get text regions with bounding boxes for advanced processing"""
        try:
            if file_path.lower().endswith('.pdf'):
                images = pdf2image.convert_from_path(file_path)
                if images:
                    image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
                else:
                    return []
            else:
                image = cv2.imread(file_path)

            if image is None:
                return []

            # Preprocess image
            processed = self._preprocess_image(image)

            # Get detailed OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)

            regions = []
            for i in range(len(ocr_data['text'])):
                if ocr_data['conf'][i] > 30:  # Filter low confidence text
                    regions.append({
                        'text': ocr_data['text'][i],
                        'confidence': ocr_data['conf'][i],
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    })

            return regions

        except Exception as e:
            print(f"Error getting text regions: {e}")
            return []

    def validate_extraction_quality(self, extracted_data: Dict, confidence: float) -> Dict:
        """Validate the quality of extracted data"""
        quality_score = 0
        issues = []

        # Check confidence
        if confidence > 80:
            quality_score += 30
        elif confidence > 60:
            quality_score += 20
        elif confidence > 40:
            quality_score += 10
        else:
            issues.append("Low OCR confidence")

        # Check if essential fields are present
        essential_fields = ['student_name', 'institution', 'course']
        for field in essential_fields:
            if extracted_data.get(field):
                quality_score += 20
            else:
                issues.append(f"Missing {field}")

        # Check data quality
        if extracted_data.get('year') and len(extracted_data['year']) == 4:
            quality_score += 10

        return {
            'quality_score': min(quality_score, 100),
            'issues': issues,
            'reliable': quality_score >= 60
        }
