import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Handles post-processing of OCR text to extract structured food data.
    """
    
    def __init__(self):
        # Common patterns for nutritional information
        self.calorie_patterns = [
            r'calories?\s*:?\s*(\d+)',
            r'energy\s*:?\s*(\d+)\s*(?:kcal|cal)',
            r'(\d+)\s*(?:kcal|cal)',
            r'caloric\s+value\s*:?\s*(\d+)',
        ]
        
        # Common patterns for serving size
        self.serving_patterns = [
            r'serving\s+size\s*:?\s*([^\n]+)',
            r'portion\s*:?\s*([^\n]+)',
            r'per\s+(\d+\s*(?:g|ml|oz|cup))',
        ]
        
        # Ingredient patterns
        self.ingredient_patterns = [
            r'ingredients?\s*:?\s*([^\n]+(?:\n(?![A-Z]{2,})[^\n]+)*)',
            r'contains?\s*:?\s*([^\n]+)',
        ]
    
    def extract_food_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured food data from OCR text.
        
        Args:
            text: Raw OCR text
        
        Returns:
            Dictionary containing extracted food information
        """
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Extract different components
        calories = self._extract_calories(cleaned_text)
        serving_size = self._extract_serving_size(cleaned_text)
        ingredients = self._extract_ingredients(cleaned_text)
        nutrition_facts = self._extract_nutrition_facts(cleaned_text)
        allergens = self._extract_allergens(cleaned_text)
        
        return {
            "calories": calories,
            "serving_size": serving_size,
            "ingredients": ingredients,
            "nutrition_facts": nutrition_facts,
            "allergens": allergens
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize OCR text.
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might have been misread
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\%\/]', '', text)
        return text.strip()
    
    def _extract_calories(self, text: str) -> Dict[str, Any]:
        """
        Extract calorie information.
        """
        text_lower = text.lower()
        
        for pattern in self.calorie_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    calorie_value = int(match.group(1))
                    logger.info(f"Found calories: {calorie_value}")
                    return {
                        "value": calorie_value,
                        "unit": "kcal",
                        "found": True
                    }
                except (ValueError, IndexError):
                    continue
        
        logger.warning("No calorie information found")
        return {
            "value": None,
            "unit": "kcal",
            "found": False
        }
    
    def _extract_serving_size(self, text: str) -> Dict[str, Any]:
        """
        Extract serving size information.
        """
        text_lower = text.lower()
        
        for pattern in self.serving_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                serving = match.group(1).strip()
                logger.info(f"Found serving size: {serving}")
                return {
                    "value": serving,
                    "found": True
                }
        
        logger.warning("No serving size found")
        return {
            "value": None,
            "found": False
        }
    
    def _extract_ingredients(self, text: str) -> Dict[str, Any]:
        """
        Extract ingredients list.
        """
        for pattern in self.ingredient_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                ingredients_text = match.group(1).strip()
                # Split by comma or semicolon
                ingredient_list = re.split(r'[,;]', ingredients_text)
                ingredient_list = [ing.strip() for ing in ingredient_list if ing.strip()]
                
                logger.info(f"Found {len(ingredient_list)} ingredients")
                return {
                    "list": ingredient_list,
                    "raw": ingredients_text,
                    "found": True
                }
        
        logger.warning("No ingredients found")
        return {
            "list": [],
            "raw": None,
            "found": False
        }
    
    def _extract_nutrition_facts(self, text: str) -> Dict[str, Any]:
        """
        Extract detailed nutrition facts.
        """
        nutrition = {}
        text_lower = text.lower()
        
        # Common nutritional components
        nutrients = {
            'protein': [r'protein\s*:?\s*(\d+\.?\d*)\s*g', r'proteins?\s*(\d+\.?\d*)'],
            'fat': [r'(?:total\s+)?fat\s*:?\s*(\d+\.?\d*)\s*g', r'fats?\s*(\d+\.?\d*)'],
            'carbohydrates': [r'(?:total\s+)?carbohydrate\s*:?\s*(\d+\.?\d*)\s*g', r'carbs?\s*(\d+\.?\d*)'],
            'sugar': [r'sugars?\s*:?\s*(\d+\.?\d*)\s*g', r'sugar\s*(\d+\.?\d*)'],
            'fiber': [r'(?:dietary\s+)?fiber\s*:?\s*(\d+\.?\d*)\s*g', r'fibre\s*(\d+\.?\d*)'],
            'sodium': [r'sodium\s*:?\s*(\d+\.?\d*)\s*(?:mg|g)', r'salt\s*(\d+\.?\d*)'],
        }
        
        for nutrient, patterns in nutrients.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        nutrition[nutrient] = {
                            "value": value,
                            "unit": "g" if nutrient != 'sodium' else "mg"
                        }
                        break
                    except (ValueError, IndexError):
                        continue
        
        logger.info(f"Extracted nutrition facts for {len(nutrition)} nutrients")
        return nutrition
    
    def _extract_allergens(self, text: str) -> Dict[str, Any]:
        """
        Extract allergen information.
        """
        text_lower = text.lower()
        
        common_allergens = [
            'milk', 'eggs', 'fish', 'shellfish', 'tree nuts', 'peanuts',
            'wheat', 'soybeans', 'soy', 'gluten', 'sesame', 'mustard'
        ]
        
        found_allergens = []
        
        # Look for allergen declaration section
        allergen_section = re.search(
            r'(?:contains?|allergens?|may contain)\s*:?\s*([^\n]+)',
            text_lower,
            re.IGNORECASE
        )
        
        if allergen_section:
            allergen_text = allergen_section.group(1)
            for allergen in common_allergens:
                if allergen in allergen_text:
                    found_allergens.append(allergen)
        
        # Also check full text for allergen mentions
        else:
            for allergen in common_allergens:
                pattern = r'\b' + allergen + r'\b'
                if re.search(pattern, text_lower):
                    found_allergens.append(allergen)
        
        logger.info(f"Found {len(found_allergens)} allergens")
        return {
            "list": list(set(found_allergens)),  # Remove duplicates
            "found": len(found_allergens) > 0
        }
