import pytesseract
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)


class OCRServiceAdvanced:
    """
    Advanced OCR service with multi-pass strategy for better accuracy.
    Use this for shiny packages and difficult images.
    """
    
    def __init__(self):
        # Try different PSM modes for best results
        self.psm_modes = [
            6,   # Single uniform block of text (default, good for labels)
            3,   # Fully automatic page segmentation
            4,   # Single column of text
            11,  # Sparse text (good for scattered text)
            12,  # Sparse text with OSD (orientation detection)
        ]
    
    def extract_text_robust(self, image, preprocessed_variations=None):
        """
        Multi-pass OCR with different settings. Returns best result.
        
        Args:
            image: Primary preprocessed image
            preprocessed_variations: Dict of alternative preprocessed images
        
        Returns:
            Best extracted text
        """
        results = []
        
        # If we have multiple preprocessing variations, try them all
        if preprocessed_variations:
            for method_name, img in preprocessed_variations.items():
                for psm in self.psm_modes:
                    result = self._ocr_single_pass(img, psm, method_name)
                    if result:
                        results.append(result)
        else:
            # Just use the single image with different PSM modes
            for psm in self.psm_modes:
                result = self._ocr_single_pass(image, psm, 'default')
                if result:
                    results.append(result)
        
        if not results:
            logger.warning("No OCR results from any method")
            return ""
        
        # Return result with highest confidence
        best = max(results, key=lambda x: x['confidence'])
        logger.info(f"Best result from {best['method']} with {best['confidence']:.1f}% confidence")
        
        return best['text']
    
    def _ocr_single_pass(self, image, psm_mode, method_name):
        """
        Run OCR once with specific settings and return result with confidence.
        """
        try:
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Configure tesseract
            config = f'--oem 3 --psm {psm_mode} -l eng'
            
            # Get text
            text = pytesseract.image_to_string(pil_image, config=config)
            
            # Get confidence scores
            data = pytesseract.image_to_data(pil_image, config=config, 
                                            output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count words detected
            word_count = len([w for w in data['text'] if w.strip()])
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'word_count': word_count,
                'method': f'{method_name}_psm{psm_mode}'
            }
            
        except Exception as e:
            logger.error(f"OCR pass failed for {method_name}_psm{psm_mode}: {str(e)}")
            return None
    
    def extract_text(self, image):
        """
        Standard extraction (backward compatible with original OCRService).
        Uses best PSM mode automatically.
        """
        return self.extract_text_robust(image)
    
    def extract_with_best_psm(self, image):
        """
        Try all PSM modes and return best result.
        """
        best_result = None
        best_confidence = 0
        
        for psm in self.psm_modes:
            config = f'--oem 3 --psm {psm} -l eng'
            
            try:
                if isinstance(image, np.ndarray):
                    pil_image = Image.fromarray(image)
                else:
                    pil_image = image
                
                data = pytesseract.image_to_data(pil_image, config=config,
                                                output_type=pytesseract.Output.DICT)
                
                confidences = [int(c) for c in data['conf'] if int(c) > 0]
                avg_conf = sum(confidences) / len(confidences) if confidences else 0
                
                if avg_conf > best_confidence:
                    best_confidence = avg_conf
                    best_result = pytesseract.image_to_string(pil_image, config=config)
                    best_psm = psm
                    
            except Exception as e:
                logger.error(f"PSM {psm} failed: {str(e)}")
                continue
        
        logger.info(f"Best PSM mode: {best_psm} with {best_confidence:.1f}% confidence")
        return best_result if best_result else ""
    
    def extract_with_whitelist(self, image, whitelist_chars=None):
        """
        Extract text with character whitelist to reduce errors.
        Useful when you know what characters to expect.
        
        Args:
            image: Preprocessed image
            whitelist_chars: String of allowed characters (None = alphanumeric + common punctuation)
        """
        if whitelist_chars is None:
            # Default: alphanumeric + common punctuation for food labels
            whitelist_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,%()- '
        
        config = f'--oem 3 --psm 6 -c tessedit_char_whitelist={whitelist_chars}'
        
        try:
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            text = pytesseract.image_to_string(pil_image, config=config)
            return text
            
        except Exception as e:
            logger.error(f"Whitelist OCR failed: {str(e)}")
            return self.extract_text(image)  # Fallback to standard
    
    def extract_by_regions(self, image, min_confidence=30):
        """
        Detect text regions and process each separately.
        Can improve accuracy for complex layouts.
        
        Returns:
            List of text segments with positions
        """
        try:
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(pil_image, config='--oem 3 --psm 11',
                                            output_type=pytesseract.Output.DICT)
            
            # Group by blocks/paragraphs
            regions = []
            current_block = {'text': [], 'bbox': None}
            
            for i in range(len(data['text'])):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > min_confidence and text:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    current_block['text'].append(text)
                    
                    # Update bounding box
                    if current_block['bbox'] is None:
                        current_block['bbox'] = [x, y, x+w, y+h]
                    else:
                        current_block['bbox'][0] = min(current_block['bbox'][0], x)
                        current_block['bbox'][1] = min(current_block['bbox'][1], y)
                        current_block['bbox'][2] = max(current_block['bbox'][2], x+w)
                        current_block['bbox'][3] = max(current_block['bbox'][3], y+h)
            
            if current_block['text']:
                regions.append({
                    'text': ' '.join(current_block['text']),
                    'bbox': current_block['bbox']
                })
            
            return regions
            
        except Exception as e:
            logger.error(f"Region-based OCR failed: {str(e)}")
            return [{'text': self.extract_text(image), 'bbox': None}]
    
    def get_detailed_results(self, image):
        """
        Get word-level results with confidence scores and positions.
        Useful for debugging and quality assessment.
        """
        try:
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            else:
                pil_image = image
            
            data = pytesseract.image_to_data(pil_image, config='--oem 3 --psm 6',
                                            output_type=pytesseract.Output.DICT)
            
            words = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:
                    words.append({
                        'text': text,
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })
            
            # Calculate overall statistics
            confidences = [w['confidence'] for w in words if w['confidence'] > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'words': words,
                'total_words': len(words),
                'average_confidence': round(avg_confidence, 2),
                'full_text': ' '.join([w['text'] for w in words])
            }
            
        except Exception as e:
            logger.error(f"Detailed results failed: {str(e)}")
            return {
                'words': [],
                'total_words': 0,
                'average_confidence': 0,
                'full_text': self.extract_text(image)
            }
    
    def test_tesseract(self):
        """
        Test if Tesseract is properly installed.
        """
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return {
                'installed': True,
                'version': str(version),
                'message': f"Tesseract {version} is working correctly"
            }
        except Exception as e:
            logger.error(f"Tesseract not found: {str(e)}")
            return {
                'installed': False,
                'version': None,
                'message': f"Tesseract not found. Please install it. Error: {str(e)}"
            }
