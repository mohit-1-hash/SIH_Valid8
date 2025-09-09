"""
Certificate Verification System Utilities Package

This package contains utility modules for:
- OCR processing with Tesseract
- Watermark detection using OpenCV  
- Digital signature verification
- DigiLocker API integration
"""

from .ocr_processor import OCRProcessor
from .watermark_detector import WatermarkDetector
from .signature_verifier import SignatureVerifier
from .digilocker_api import DigilockerAPI

__all__ = [
    'OCRProcessor',
    'WatermarkDetector', 
    'SignatureVerifier',
    'DigilockerAPI'
]
