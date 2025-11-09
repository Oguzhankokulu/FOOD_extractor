import pytesseract
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """
    Handles OCR text extraction using Tesseract.
    """
    
    def __init__(self):
        # Configure tesseract path if needed (uncomment and modify if tesseract is not in PATH)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        
        # OCR configuration with Turkish and English support
        # --oem 3: Use default OCR Engine Mode (LSTM neural net)
        # --psm 6: Assume a single uniform block of text
        # -l tur+eng: Use Turkish and English languages
        self.config = '--oem 3 --psm 6 -l tur+eng'
    
    def extract_text(self, image):
        """
        Extract text from preprocessed image using Tesseract OCR.
        
        Args:
            image: Preprocessed image (numpy array)
        
        Returns:
            Extracted text as string
        """
        try:
            # Convert numpy array to PIL Image for pytesseract
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image, config=self.config)
            
            logger.info(f"OCR extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error during OCR: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_text_with_confidence(self, image):
        """
        Extract text with confidence scores and bounding boxes.
        Useful for advanced processing and debugging.
        
        Args:
            image: Preprocessed image
        
        Returns:
            Dictionary with detailed OCR data
        """
        try:
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(pil_image, config=self.config, output_type=pytesseract.Output.DICT)
            
            # Filter out low confidence detections
            filtered_text = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Only keep text with >30% confidence
                    text = data['text'][i].strip()
                    if text:
                        filtered_text.append(text)
            
            return {
                'text': ' '.join(filtered_text),
                'full_data': data,
                'word_count': len(filtered_text)
            }
            
        except Exception as e:
            logger.error(f"Error during detailed OCR: {str(e)}")
            # Fallback to simple extraction
            return {
                'text': self.extract_text(image),
                'full_data': None,
                'word_count': 0
            }
    
    def test_tesseract(self):
        """
        Test if Tesseract is properly installed and accessible.
        
        Returns:
            Tesseract version string or error message
        """
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return str(version)
        except Exception as e:
            logger.error(f"Tesseract not found: {str(e)}")
            return f"Error: {str(e)}"
