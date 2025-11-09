import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageProcessorAdvanced:
    """
    Advanced image preprocessing for challenging surfaces (shiny packages, glare, angles).
    Use this instead of ImageProcessor for better results on real food packages.
    """
    
    def __init__(self):
        self.target_width = 1500
    
    def preprocess(self, image):
        """
        Main preprocessing method (backward compatible).
        Calls preprocess_shiny_package for best results.
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            Preprocessed image ready for OCR
        """
        return self.preprocess_shiny_package(image)
    
    def preprocess_shiny_package(self, image):
        """
        Optimized preprocessing pipeline for shiny food packages.
        Handles glare, reflections, and perspective issues.
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            Preprocessed image ready for OCR
        """
        try:
            # Step 1: Resize
            image = self._resize_image(image)
            
            # Step 2: Remove glare (if color image)
            if len(image.shape) == 3:
                image = self._remove_glare(image)
            
            # Step 3: Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Step 4: Bilateral filter (better edge preservation than NLM)
            denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
            
            # Step 5: Aggressive CLAHE for shiny surfaces
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Step 6: Unsharp masking (sharpen text edges)
            sharpened = self._unsharp_mask(enhanced)
            
            # Step 7: Adaptive thresholding with larger block size
            thresh = cv2.adaptiveThreshold(
                sharpened,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                15,  # Larger block size for varied lighting
                2
            )
            
            # Step 8: Deskew (correct rotation)
            deskewed = self._deskew_image(thresh)
            
            # Step 9: Morphological cleaning
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(deskewed, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            logger.info("Advanced preprocessing completed successfully")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error in advanced preprocessing: {str(e)}")
            # Fallback to basic grayscale
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def preprocess_multiple_methods(self, image):
        """
        Generate multiple preprocessed versions for multi-pass OCR.
        Try OCR on all versions and pick best result.
        
        Args:
            image: Input image
        
        Returns:
            Dictionary of preprocessed images with different methods
        """
        results = {}
        
        # Method 1: Optimized for shiny packages
        results['shiny_optimized'] = self.preprocess_shiny_package(image)
        
        # Method 2: Standard preprocessing
        results['standard'] = self._standard_preprocess(image)
        
        # Method 3: High contrast
        results['high_contrast'] = self._high_contrast_preprocess(image)
        
        # Method 4: Inverted (for light text on dark background)
        results['inverted'] = cv2.bitwise_not(results['standard'])
        
        # Method 5: Multiple thresholds
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Otsu's method
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results['otsu'] = otsu
        
        # Adaptive mean
        adaptive_mean = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
        )
        results['adaptive_mean'] = adaptive_mean
        
        return results
    
    def _remove_glare(self, image):
        """
        Remove glare and reflections from shiny surfaces.
        Uses LAB color space for better separation of brightness.
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE only to L channel (brightness)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge back and convert to BGR
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        logger.info("Glare removal applied")
        return result
    
    def _deskew_image(self, image):
        """
        Automatically detect and correct image rotation/skew.
        Tesseract works best with horizontal text.
        """
        # Find all non-zero points
        coords = np.column_stack(np.where(image > 0))
        
        if len(coords) == 0:
            return image
        
        # Get rotation angle
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only correct if angle is significant (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image
        
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        logger.info(f"Image deskewed by {angle:.2f} degrees")
        return rotated
    
    def _unsharp_mask(self, image, sigma=2.0, strength=1.5):
        """
        Sharpen image to enhance text edges.
        """
        # Create blurred version
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        
        # Sharpened = Original + (Original - Blurred) * strength
        sharpened = cv2.addWeighted(image, strength, blurred, -strength + 1, 0)
        
        return sharpened
    
    def _resize_image(self, image):
        """
        Resize image to optimal size for OCR.
        """
        height, width = image.shape[:2]
        
        if width < self.target_width * 0.5 or width > self.target_width * 2:
            aspect_ratio = height / width
            new_width = self.target_width
            new_height = int(new_width * aspect_ratio)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            logger.info(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            return resized
        
        return image
    
    def _standard_preprocess(self, image):
        """
        Standard preprocessing pipeline (original method).
        """
        image = self._resize_image(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(denoised)
        
        thresh = cv2.adaptiveThreshold(
            contrast_enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def _high_contrast_preprocess(self, image):
        """
        High contrast preprocessing for faded text.
        """
        image = self._resize_image(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Very aggressive CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)
        
        # Sharpen
        sharpened = self._unsharp_mask(enhanced, sigma=1.5, strength=2.0)
        
        # Threshold
        _, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def check_image_quality(self, image):
        """
        Check if image is suitable for OCR and provide feedback.
        
        Returns:
            Dictionary with quality metrics and issues
        """
        issues = []
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Check brightness
        mean_brightness = np.mean(gray)
        if mean_brightness < 40:
            issues.append("Image too dark - use better lighting")
        elif mean_brightness > 215:
            issues.append("Image too bright/overexposed - reduce lighting")
        
        # Check blur (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            issues.append("Image too blurry - hold camera steady and focus on text")
        
        # Check contrast
        contrast = gray.std()
        if contrast < 30:
            issues.append("Low contrast - improve lighting or try different angle")
        
        # Check resolution
        height, width = gray.shape
        if width < 800 or height < 600:
            issues.append("Image resolution too low - get closer to the text")
        
        quality_score = 100
        if mean_brightness < 40 or mean_brightness > 215:
            quality_score -= 30
        if laplacian_var < 100:
            quality_score -= 40
        if contrast < 30:
            quality_score -= 20
        if width < 800:
            quality_score -= 10
        
        return {
            'suitable': len(issues) == 0,
            'quality_score': max(0, quality_score),
            'issues': issues,
            'metrics': {
                'brightness': round(mean_brightness, 2),
                'blur_score': round(laplacian_var, 2),
                'contrast': round(contrast, 2),
                'resolution': f"{width}x{height}"
            }
        }
