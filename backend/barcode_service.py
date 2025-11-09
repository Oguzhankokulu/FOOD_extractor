import cv2
import numpy as np
import requests
import logging
from pyzbar import pyzbar

logger = logging.getLogger(__name__)


class BarcodeService:
    """
    Handles barcode detection and product lookup via OpenFoodFacts API.
    """
    
    def __init__(self):
        self.api_base_url = "https://tr.openfoodfacts.org/api/v2/product"
    
    def detect_barcode(self, image):
        """
        Detect barcode from image.
        
        Args:
            image: Input image as numpy array (BGR format)
        
        Returns:
            Barcode string if found, None otherwise
        """
        try:
            # Convert to grayscale for better barcode detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Detect barcodes
            barcodes = pyzbar.decode(gray)
            
            if barcodes:
                # Return the first barcode found
                barcode_data = barcodes[0].data.decode('utf-8')
                barcode_type = barcodes[0].type
                logger.info(f"Barcode detected: {barcode_data} (Type: {barcode_type})")
                return barcode_data
            
            logger.info("No barcode detected in image")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting barcode: {str(e)}")
            return None
    
    def get_product_info(self, barcode):
        """
        Fetch product information from OpenFoodFacts Turkey database.
        
        Args:
            barcode: Barcode string
        
        Returns:
            Dictionary with product information or None if not found
        """
        try:
            url = f"{self.api_base_url}/{barcode}"
            logger.info(f"Fetching product from OpenFoodFacts: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1 and data.get('product'):
                    product = data['product']
                    logger.info(f"Product found: {product.get('product_name', 'Unknown')}")
                    return self._extract_product_data(product)
                else:
                    logger.warning(f"Product not found for barcode: {barcode}")
                    return None
            else:
                logger.warning(f"OpenFoodFacts API returned status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("OpenFoodFacts API timeout")
            return None
        except Exception as e:
            logger.error(f"Error fetching product info: {str(e)}")
            return None
    
    def _extract_product_data(self, product):
        """
        Extract and structure product data from OpenFoodFacts response.
        
        Args:
            product: Product dictionary from OpenFoodFacts API
        
        Returns:
            Structured product data matching our format
        """
        # Get nutriments
        nutriments = product.get('nutriments', {})
        
        # Extract calories
        calories_value = nutriments.get('energy-kcal_100g') or nutriments.get('energy-kcal')
        calories_serving = nutriments.get('energy-kcal_serving')
        
        # Extract serving size
        serving_size = product.get('serving_size') or product.get('serving_quantity')
        
        # Extract ingredients
        ingredients_text = product.get('ingredients_text') or product.get('ingredients_text_tr')
        ingredients_list = []
        if ingredients_text:
            # Split by comma or semicolon
            ingredients_list = [ing.strip() for ing in ingredients_text.replace(';', ',').split(',')]
        
        # Extract allergens
        allergens_tags = product.get('allergens_tags', [])
        allergens_list = [tag.replace('en:', '').replace('-', ' ') for tag in allergens_tags]
        
        # Build structured data
        structured_data = {
            "source": "openfoodfacts",
            "barcode": product.get('code'),
            "product_name": product.get('product_name') or product.get('product_name_tr'),
            "brands": product.get('brands'),
            "categories": product.get('categories'),
            "image_url": product.get('image_url'),
            "calories": {
                "value": calories_value,
                "value_serving": calories_serving,
                "unit": "kcal",
                "found": calories_value is not None
            },
            "serving_size": {
                "value": serving_size,
                "found": serving_size is not None
            },
            "ingredients": {
                "list": ingredients_list,
                "raw": ingredients_text,
                "found": bool(ingredients_text)
            },
            "nutrition_facts": self._extract_nutrition_facts(nutriments),
            "allergens": {
                "list": allergens_list,
                "found": bool(allergens_list)
            },
            "labels": product.get('labels_tags', []),
            "nova_group": product.get('nova_group'),
            "nutriscore_grade": product.get('nutriscore_grade')
        }
        
        return structured_data
    
    def _extract_nutrition_facts(self, nutriments):
        """
        Extract nutrition facts from nutriments data.
        """
        nutrition = {}
        
        # Mapping of nutrient names
        nutrient_map = {
            'protein': ['proteins_100g', 'proteins'],
            'fat': ['fat_100g', 'fat'],
            'saturated_fat': ['saturated-fat_100g', 'saturated-fat'],
            'carbohydrates': ['carbohydrates_100g', 'carbohydrates'],
            'sugars': ['sugars_100g', 'sugars'],
            'fiber': ['fiber_100g', 'fiber'],
            'sodium': ['sodium_100g', 'sodium'],
            'salt': ['salt_100g', 'salt']
        }
        
        for nutrient, keys in nutrient_map.items():
            for key in keys:
                value = nutriments.get(key)
                if value is not None:
                    unit = "mg" if nutrient in ['sodium', 'salt'] else "g"
                    nutrition[nutrient] = {
                        "value": value,
                        "unit": unit
                    }
                    break
        
        return nutrition
    
    def scan_and_fetch(self, image):
        """
        Detect barcode and fetch product information in one call.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            Product data if found, None otherwise
        """
        barcode = self.detect_barcode(image)
        if barcode:
            return self.get_product_info(barcode)
        return None
