# Barcode Scanning Setup Guide

## New Features Added

1. **Barcode Detection**: Automatically detects and scans barcodes in images
2. **OpenFoodFacts Integration**: Fetches product data from OpenFoodFacts Turkey database
3. **Turkish Language Support**: OCR now supports both Turkish and English
4. **Smart Fallback**: If barcode not found, automatically falls back to OCR

## Additional Dependencies Required

### 1. Python Packages

Install the new packages:

```bash
cd backend
source venv/bin/activate.fish  # or your activation command
pip install pyzbar requests
```

Or reinstall from updated requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. System Library for Barcode Scanning

**pyzbar** requires the ZBar library:

#### Ubuntu/Debian:
```bash
sudo apt-get install libzbar0
```

#### macOS:
```bash
brew install zbar
```

#### Windows:
Download and install from: http://zbar.sourceforge.net/

### 3. Turkish Language for Tesseract

Install Turkish language pack:

#### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr-tur
```

#### macOS:
```bash
brew install tesseract-lang
```

#### Windows:
During Tesseract installation, select Turkish language pack, or download from:
https://github.com/tesseract-ocr/tessdata

Verify installation:
```bash
tesseract --list-langs
# Should show both 'eng' and 'tur'
```

## How It Works

### Processing Flow

```
Image Upload
    ↓
1. Barcode Detection
    ├─ Barcode Found? 
    │   ├─ YES → Fetch from OpenFoodFacts Turkey
    │   │         ├─ Found? → Return product data ✓
    │   │         └─ Not Found? → Continue to OCR
    │   └─ NO → Continue to OCR
    ↓
2. OCR Processing (Turkish + English)
    ├─ Preprocess image
    ├─ Extract text
    └─ Parse structured data → Return ✓
```

### OpenFoodFacts Turkey API

The system uses: `https://tr.openfoodfacts.org/api/v2/product/{barcode}`

**Data Retrieved:**
- Product name (Turkish)
- Brand
- Ingredients (Turkish)
- Nutrition facts per 100g
- Allergens
- Nutri-Score grade
- NOVA group
- Product image
- Labels (organic, vegan, etc.)

### Benefits of Barcode Scanning

1. **Instant Results**: No OCR processing needed
2. **High Accuracy**: Database information is verified
3. **Complete Data**: Often more complete than OCR
4. **Multiple Languages**: Product names in Turkish
5. **Additional Info**: Nutri-Score, NOVA group, labels

## Testing

### Test with a Turkish Product

1. Take a photo of a Turkish food product with a visible barcode
2. Upload to the app
3. Check the response - should show "📊 From Barcode"

### Test OCR Fallback

1. Take a photo without a barcode (or cover the barcode)
2. Upload to the app
3. Should automatically fall back to OCR
4. Should show "🔍 From OCR"

### API Test

```bash
# Test barcode endpoint with a Turkish product
curl -X POST "http://localhost:8000/upload-image" \
  -F "file=@path/to/barcode_image.jpg"
```

Example response (barcode found):
```json
{
  "success": true,
  "message": "Product found via barcode from OpenFoodFacts",
  "method": "barcode",
  "data": {
    "source": "openfoodfacts",
    "barcode": "8690504531234",
    "product_name": "Ürün Adı",
    "brands": "Marka",
    "calories": {
      "value": 250,
      "unit": "kcal",
      "found": true
    },
    ...
  }
}
```

Example response (OCR fallback):
```json
{
  "success": true,
  "message": "Image processed successfully via OCR",
  "method": "ocr",
  "data": {
    "source": "ocr",
    ...
  }
}
```

## Common Issues

### Issue: "No module named 'pyzbar'"
**Solution**: Install pyzbar and zbar library
```bash
pip install pyzbar
sudo apt-get install libzbar0  # Linux
brew install zbar              # macOS
```

### Issue: "No module named 'requests'"
**Solution**: Install requests
```bash
pip install requests
```

### Issue: Tesseract error "Failed loading language 'tur'"
**Solution**: Install Turkish language pack
```bash
sudo apt-get install tesseract-ocr-tur
```

Verify:
```bash
tesseract --list-langs
```

### Issue: Barcode not detected
**Possible causes:**
1. Barcode is too small in image - get closer
2. Barcode is blurry - focus properly
3. Poor lighting - improve illumination
4. Barcode is damaged - try different angle

### Issue: Product not found in OpenFoodFacts
This is normal - not all products are in the database. The system will automatically fall back to OCR.

## Supported Barcode Types

- EAN-13 (most common in Turkey/Europe)
- EAN-8
- UPC-A
- UPC-E
- Code 128
- Code 39
- QR Code
- And more...

## Performance

### Barcode Method:
- Detection: ~0.5 seconds
- API fetch: ~0.5-1 second
- **Total: ~1-1.5 seconds**

### OCR Method (fallback):
- Preprocessing: ~0.5 seconds
- OCR: ~1-2 seconds
- Post-processing: ~0.1 seconds
- **Total: ~2-3 seconds**

**Barcode is 50% faster when available!**

## Privacy Note

When using barcode scanning:
- Barcode is sent to OpenFoodFacts API (public database)
- No image is sent, only the barcode number
- OCR processing remains 100% local

## Next Steps

1. Install dependencies (see above)
2. Restart backend server
3. Test with Turkish products
4. Enjoy faster, more accurate results!

## Turkish Language Examples

The system now understands Turkish terms:

**Calories:**
- "Enerji: 250 kcal"
- "Kalori: 250"

**Ingredients:**
- "İçindekiler: un, şeker, süt"
- "Bileşenler: ..."

**Allergens:**
- "Alerjenler: süt, yumurta"
- "İçerebilir: fındık"

**Nutrition:**
- "Protein: 5g"
- "Yağ: 12g"
- "Karbonhidrat: 30g"

The regex patterns in `text_processor.py` work with both Turkish and English terms automatically!
