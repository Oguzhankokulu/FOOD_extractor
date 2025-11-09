# 🍎 Food Package OCR Scanner

A web application that extracts ingredients and nutritional information from food package images using OCR technology.

## Features

- 📷 **Camera Support**: Take photos directly from your device's camera
- 📁 **Image Upload**: Upload existing images from your device
- 🔍 **OCR Processing**: Extract text from images using Tesseract OCR
- 🎨 **Image Enhancement**: Advanced preprocessing with OpenCV for better accuracy
- 📊 **Structured Data**: Automatically extract:
  - Calories and nutritional facts
  - Ingredients list
  - Serving size
  - Allergen information
- 💅 **Modern UI**: Clean, responsive interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenCV**: Image preprocessing and enhancement
- **Tesseract OCR**: Optical character recognition
- **Python regex**: Text post-processing and data extraction

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **Vanilla JavaScript**: No frameworks needed
- **Camera API**: Direct camera access

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
2. **Tesseract OCR**
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /home/oguzhan/Projects/FOOD_extractor
```

### 2. Set Up Backend

#### Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Virtual Environment

- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Tesseract Installation

Test that Tesseract is properly installed:

```bash
tesseract --version
```

If this command fails, you need to install Tesseract OCR (see Prerequisites).

## Running the Application

### 1. Start the Backend Server

From the `backend` directory with the virtual environment activated:

```bash
python main.py
```

The server will start on `http://localhost:8000`

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Open the Frontend

Open the `frontend/index.html` file in your web browser:

```bash
# From the project root
cd frontend
# Open in your default browser
xdg-open index.html  # Linux
open index.html      # macOS
start index.html     # Windows
```

Or simply open the file directly in your browser by double-clicking it.

## Usage

1. **Choose Input Method**:
   - Click "Open Camera" to take a photo
   - Click "Choose File" to upload an image

2. **Capture/Select Image**:
   - If using camera: Click "Capture" when ready
   - If uploading: Select an image file

3. **Process Image**:
   - Click "Process Image" button
   - Wait for processing (usually 2-5 seconds)

4. **View Results**:
   - See extracted nutritional information
   - View ingredients list
   - Check allergen warnings
   - Toggle "Show JSON" for raw data

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Main Endpoint

**POST /upload-image**
- Upload an image for OCR processing
- Content-Type: `multipart/form-data`
- Field: `file` (image file)
- Returns: JSON with extracted food data

Example response:
```json
{
  "success": true,
  "message": "Image processed successfully",
  "data": {
    "calories": {
      "value": 250,
      "unit": "kcal",
      "found": true
    },
    "serving_size": {
      "value": "100g",
      "found": true
    },
    "ingredients": {
      "list": ["wheat flour", "sugar", "vegetable oil"],
      "raw": "wheat flour, sugar, vegetable oil",
      "found": true
    },
    "nutrition_facts": {
      "protein": {"value": 5.0, "unit": "g"},
      "fat": {"value": 12.0, "unit": "g"}
    },
    "allergens": {
      "list": ["wheat", "milk"],
      "found": true
    }
  }
}
```

## Project Structure

```
FOOD_extractor/
├── backend/
│   ├── main.py                      # FastAPI application
│   ├── image_processor.py           # Basic OpenCV image preprocessing
│   ├── image_processor_advanced.py  # Advanced preprocessing (for shiny packages)
│   ├── ocr_service.py               # Basic Tesseract OCR wrapper
│   ├── ocr_service_advanced.py      # Advanced multi-pass OCR
│   ├── text_processor.py            # Regex-based text extraction
│   ├── requirements.txt             # Python dependencies
│   └── .gitignore
├── frontend/
│   ├── index.html                   # Main HTML file
│   ├── styles.css                   # Styling
│   └── app.js                       # Frontend logic
├── README.md                        # This file
├── ALGORITHM_DOCUMENTATION.md       # Detailed algorithm explanations
└── UPGRADE_GUIDE.md                 # How to use advanced OCR features
```

## Troubleshooting

### "Import cv2 could not be resolved" or similar errors
These are just linting warnings. The packages will be installed when you run `pip install -r requirements.txt`.

### "Tesseract not found" error
Make sure Tesseract is installed and in your system PATH. If not, you can specify the path in `backend/ocr_service.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
```

### CORS errors in browser
Make sure the backend server is running and accessible at `http://localhost:8000`.

### Poor OCR accuracy
**For shiny packages and difficult images**, see the detailed improvement guide:
- **Read `ALGORITHM_DOCUMENTATION.md`** for understanding the algorithms and improvement strategies
- **Read `UPGRADE_GUIDE.md`** for step-by-step instructions to use advanced OCR features

Quick tips:
- Ensure the image is clear and well-lit (but not overexposed)
- Make sure the text is in focus
- Try to flatten the package (tape it to a wall)
- Avoid direct glare - angle the package slightly away from light source
- Get close to the text to fill the frame
- The preprocessing handles most cases, but **shiny/metallic surfaces are challenging**
- **Use the advanced image processor** for shiny packages (see UPGRADE_GUIDE.md)

### Camera not working
- Grant camera permissions in your browser
- Use HTTPS or localhost (required by modern browsers)
- Check browser compatibility (modern browsers required)

## Development

### Adding New Features

**To modify image preprocessing**: Edit `backend/image_processor.py`
**To improve OCR**: Edit `backend/ocr_service.py`
**To add new extraction patterns**: Edit `backend/text_processor.py`
**To modify frontend**: Edit files in `frontend/`

### Testing

Test the API with curl:
```bash
curl -X POST "http://localhost:8000/upload-image" \
  -F "file=@/path/to/your/image.jpg"
```

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!
