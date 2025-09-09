
import cv2
import numpy as np
from typing import Dict, List, Tuple
from scipy import ndimage
import os

class WatermarkDetector:
    """Advanced watermark detection for certificate verification"""

    def __init__(self):
        self.known_watermarks = []
        self.template_path = "app/static/watermark_templates/"
        self.load_watermark_templates()

    def load_watermark_templates(self):
        """Load known watermark templates from file system"""
        if not os.path.exists(self.template_path):
            os.makedirs(self.template_path, exist_ok=True)
            return

        for filename in os.listdir(self.template_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_path = os.path.join(self.template_path, filename)
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self.known_watermarks.append({
                        'name': filename,
                        'template': template,
                        'path': template_path
                    })

    def detect_watermark(self, file_path: str) -> Dict:
        """Detect watermarks in certificate image/PDF"""
        try:
            # Load and preprocess image
            image = self._load_image(file_path)
            if image is None:
                return {'has_watermark': False, 'error': 'Could not load image'}

            # Multiple watermark detection methods
            results = {
                'has_watermark': False,
                'watermark_type': 'none',
                'confidence': 0.0,
                'detection_methods': {},
                'watermark_locations': []
            }

            # Method 1: Template matching with known watermarks
            template_result = self._detect_template_watermarks(image)
            results['detection_methods']['template_matching'] = template_result

            # Method 2: Digital watermark detection
            digital_result = self._detect_digital_watermarks(image)
            results['detection_methods']['digital_watermark'] = digital_result

            # Method 3: Text-based watermark detection
            text_result = self._detect_text_watermarks(image)
            results['detection_methods']['text_watermark'] = text_result

            # Method 4: Pattern-based detection
            pattern_result = self._detect_pattern_watermarks(image)
            results['detection_methods']['pattern_watermark'] = pattern_result

            # Method 5: Transparency/Alpha channel analysis
            alpha_result = self._detect_alpha_watermarks(file_path)
            results['detection_methods']['alpha_watermark'] = alpha_result

            # Combine results
            max_confidence = max(
                template_result.get('confidence', 0),
                digital_result.get('confidence', 0),
                text_result.get('confidence', 0),
                pattern_result.get('confidence', 0),
                alpha_result.get('confidence', 0)
            )

            results['confidence'] = max_confidence
            results['has_watermark'] = max_confidence > 0.3  # Threshold for watermark detection

            if results['has_watermark']:
                # Determine watermark type
                if template_result.get('confidence', 0) == max_confidence:
                    results['watermark_type'] = 'template'
                elif digital_result.get('confidence', 0) == max_confidence:
                    results['watermark_type'] = 'digital'
                elif text_result.get('confidence', 0) == max_confidence:
                    results['watermark_type'] = 'text'
                elif pattern_result.get('confidence', 0) == max_confidence:
                    results['watermark_type'] = 'pattern'
                else:
                    results['watermark_type'] = 'alpha'

            return results

        except Exception as e:
            return {
                'has_watermark': False,
                'error': str(e),
                'confidence': 0.0
            }

    def _load_image(self, file_path: str) -> np.ndarray:
        """Load image from file path (supports PDF and images)"""
        if file_path.lower().endswith('.pdf'):
            try:
                import pdf2image
                images = pdf2image.convert_from_path(file_path)
                if images:
                    # Convert first page to OpenCV format
                    pil_image = images[0]
                    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            except:
                return None
        else:
            return cv2.imread(file_path)

    def _detect_template_watermarks(self, image: np.ndarray) -> Dict:
        """Detect watermarks using template matching"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        best_match = {'confidence': 0.0, 'template_name': None, 'location': None}

        for watermark in self.known_watermarks:
            template = watermark['template']

            # Multi-scale template matching
            for scale in [0.5, 0.75, 1.0, 1.25, 1.5]:
                # Resize template
                h, w = template.shape
                resized_template = cv2.resize(template, (int(w * scale), int(h * scale)))

                if resized_template.shape[0] > gray.shape[0] or resized_template.shape[1] > gray.shape[1]:
                    continue

                # Template matching
                result = cv2.matchTemplate(gray, resized_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_match['confidence']:
                    best_match = {
                        'confidence': max_val,
                        'template_name': watermark['name'],
                        'location': max_loc,
                        'scale': scale
                    }

        return best_match

    def _detect_digital_watermarks(self, image: np.ndarray) -> Dict:
        """Detect digital watermarks using frequency domain analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Apply DCT (Discrete Cosine Transform)
        gray_float = np.float32(gray) / 255.0
        dct = cv2.dct(gray_float)

        # Analyze frequency components for watermark patterns
        # High frequency components often contain watermark information
        high_freq_energy = np.sum(np.abs(dct[dct.shape[0]//2:, dct.shape[1]//2:]))
        total_energy = np.sum(np.abs(dct))

        # Calculate ratio of high frequency to total energy
        if total_energy > 0:
            high_freq_ratio = high_freq_energy / total_energy
            confidence = min(high_freq_ratio * 5, 1.0)  # Scale and cap at 1.0
        else:
            confidence = 0.0

        # DWT (Discrete Wavelet Transform) analysis
        try:
            import pywt
            coeffs = pywt.dwt2(gray, 'haar')
            cA, (cH, cV, cD) = coeffs

            # Analyze high frequency coefficients
            hf_std = np.std(cH) + np.std(cV) + np.std(cD)
            if hf_std > 10:  # Threshold for watermark presence
                confidence = max(confidence, min(hf_std / 50, 1.0))
        except:
            pass

        return {
            'confidence': confidence,
            'method': 'frequency_analysis',
            'high_freq_ratio': high_freq_ratio if 'high_freq_ratio' in locals() else 0
        }

    def _detect_text_watermarks(self, image: np.ndarray) -> Dict:
        """Detect text-based watermarks"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Look for semi-transparent text overlays
        # Apply edge detection to find text patterns
        edges = cv2.Canny(gray, 50, 150)

        # Find contours that might be text
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        text_like_contours = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 10000:  # Text-like area range
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                if 0.1 < aspect_ratio < 10:  # Text-like aspect ratio
                    text_like_contours += 1

        # Calculate confidence based on number of text-like contours
        confidence = min(text_like_contours / 50, 1.0)

        # Additional check for repeated patterns (common in watermarks)
        kernel = np.ones((5, 5), np.uint8)
        morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Look for repeating patterns
        h, w = morph.shape
        pattern_matches = 0

        # Check for horizontal repetition
        for y in range(0, h, h//4):
            row = morph[y:y+50, :]
            if row.shape[0] > 0:
                # Simple pattern detection
                for i in range(0, w - 100, 50):
                    if i + 100 < w:
                        section1 = row[:, i:i+50]
                        section2 = row[:, i+50:i+100]
                        if section1.shape == section2.shape:
                            correlation = cv2.matchTemplate(section1, section2, cv2.TM_CCOEFF_NORMED)
                            if np.max(correlation) > 0.8:
                                pattern_matches += 1

        if pattern_matches > 2:
            confidence = max(confidence, 0.7)

        return {
            'confidence': confidence,
            'text_contours': text_like_contours,
            'pattern_matches': pattern_matches
        }

    def _detect_pattern_watermarks(self, image: np.ndarray) -> Dict:
        """Detect pattern-based watermarks (logos, symbols)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Use blob detection to find circular/elliptical patterns
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 100
        params.maxArea = 5000
        params.filterByCircularity = True
        params.minCircularity = 0.3

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(gray)

        # Calculate confidence based on blob characteristics
        confidence = 0.0
        if len(keypoints) > 0:
            # Large blobs might be watermark elements
            large_blobs = [kp for kp in keypoints if kp.size > 20]
            confidence = min(len(large_blobs) / 10, 1.0)

        # Additional pattern detection using corner detection
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)

        if corners is not None:
            # Analyze corner distribution
            corner_density = len(corners) / (gray.shape[0] * gray.shape[1] / 10000)
            if corner_density > 5:  # High corner density might indicate watermark
                confidence = max(confidence, min(corner_density / 20, 0.8))

        return {
            'confidence': confidence,
            'blob_count': len(keypoints),
            'corner_count': len(corners) if corners is not None else 0
        }

    def _detect_alpha_watermarks(self, file_path: str) -> Dict:
        """Detect watermarks in alpha channel or transparency"""
        try:
            if file_path.lower().endswith(('.png')):
                # PNG files can have alpha channels
                image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

                if image is not None and image.shape[2] == 4:  # Has alpha channel
                    alpha = image[:, :, 3]

                    # Analyze alpha channel for watermark patterns
                    unique_alpha_values = len(np.unique(alpha))

                    if unique_alpha_values > 10:  # Multiple transparency levels
                        # Calculate confidence based on alpha variation
                        alpha_variance = np.var(alpha)
                        confidence = min(alpha_variance / 10000, 1.0)

                        return {
                            'confidence': confidence,
                            'alpha_levels': unique_alpha_values,
                            'alpha_variance': alpha_variance
                        }

            return {'confidence': 0.0, 'reason': 'No alpha channel'}

        except Exception as e:
            return {'confidence': 0.0, 'error': str(e)}

    def create_watermark_signature(self, image_path: str) -> str:
        """Create a unique signature for watermark identification"""
        image = self._load_image(image_path)
        if image is None:
            return ""

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Create feature signature using ORB
        orb = cv2.ORB_create()
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        if descriptors is not None:
            # Create hash from descriptors
            desc_hash = hash(descriptors.tobytes())
            return str(abs(desc_hash))

        return ""

    def add_watermark_template(self, template_path: str, name: str) -> bool:
        """Add a new watermark template to the detection system"""
        try:
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is not None:
                # Save to templates directory
                save_path = os.path.join(self.template_path, f"{name}.png")
                cv2.imwrite(save_path, template)

                # Add to memory
                self.known_watermarks.append({
                    'name': f"{name}.png",
                    'template': template,
                    'path': save_path
                })

                return True
        except Exception as e:
            print(f"Error adding watermark template: {e}")

        return False
