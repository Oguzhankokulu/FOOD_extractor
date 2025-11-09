import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Handles image preprocessing using OpenCV to improve OCR accuracy.
    """
    
    def __init__(self):
        self.target_width = 1500  # Resize to this width for better OCR
    
    def preprocess(self, image):
        """
        Apply preprocessing steps to enhance text visibility.
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            Preprocessed image ready for OCR
        """
        try:
            # Step 1: Resize image for better OCR (if too small or too large)
            image = self._resize_image(image)
            
            # Step 2: Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Step 3: Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Step 4: Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast_enhanced = clahe.apply(denoised)
            
            # Step 5: Apply adaptive thresholding
            # This works better than simple thresholding for varying lighting conditions
            thresh = cv2.adaptiveThreshold(
                contrast_enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Step 6: Morphological operations to remove small noise
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            logger.info("Image preprocessing completed successfully")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            # Return grayscale as fallback
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _resize_image(self, image):
        """
        Resize image to optimal size for OCR.
        
        Args:
            image: Input image
        
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        # Only resize if image is not already close to target width
        if width < self.target_width * 0.5 or width > self.target_width * 2:
            aspect_ratio = height / width
            new_width = self.target_width
            new_height = int(new_width * aspect_ratio)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            logger.info(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            return resized
        
        return image
    
    def preprocess_multiple_methods(self, image):
        """
        Apply multiple preprocessing methods and return all results.
        Useful for trying different approaches if one doesn't work well.
        
        Args:
            image: Input image
        
        Returns:
            Dictionary of preprocessed images with different methods
        """
        results = {}
        
        # Method 1: Standard preprocessing
        results['standard'] = self.preprocess(image)
        
        # Method 2: Simple threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, simple_thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results['simple_threshold'] = simple_thresh
        
        # Method 3: Inverted (for light text on dark background)
        inverted = cv2.bitwise_not(results['standard'])
        results['inverted'] = inverted
        
        return results
