# Getting Started Checklist

Follow these steps to get your Food Package OCR Scanner up and running!

## ✅ Pre-requisites

### 1. Python Installation
- [ ] Python 3.8 or higher installed
- [ ] Check version: `python --version` or `python3 --version`

### 2. Tesseract OCR Installation

Choose your operating system:

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

#### Windows
- [ ] Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- [ ] Run installer
- [ ] Add to PATH or note installation path

- [ ] Verify installation: `tesseract --version`
  - Should show version 4.0 or higher

## 📦 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd /home/oguzhan/Projects/FOOD_extractor/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```
or
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

For **fish shell** (your current shell):
```fish
source venv/bin/activate.fish
```

For bash/zsh:
```bash
source venv/bin/activate
```

For Windows:
```bash
venv\Scripts\activate
```

- [ ] Verify activation: Prompt should show `(venv)`

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Expected packages:
- [ ] FastAPI
- [ ] Uvicorn
- [ ] OpenCV (cv2)
- [ ] Pytesseract
- [ ] Pillow
- [ ] NumPy

### 5. Test Imports (Optional but Recommended)
```bash
python -c "import cv2, pytesseract, fastapi; print('All imports successful!')"
```

### 6. Configure Tesseract Path (If Needed)

If you get "Tesseract not found" error later:

Edit `backend/ocr_service.py` and uncomment/modify:
```python
pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
```

Common paths:
- Linux: `/usr/bin/tesseract`
- macOS: `/usr/local/bin/tesseract` or `/opt/homebrew/bin/tesseract`
- Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`

## 🚀 Running the Application

### 1. Start Backend Server

From the `backend` directory with venv activated:
```bash
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

- [ ] Server running at http://localhost:8000
- [ ] Visit http://localhost:8000/docs to see API documentation

### 2. Open Frontend

Keep the backend running, then in a NEW terminal:

```bash
cd /home/oguzhan/Projects/FOOD_extractor/frontend
```

Open in browser:
```bash
# Linux
xdg-open index.html

# macOS
open index.html

# Or just double-click index.html in your file manager
```

- [ ] Frontend opens in browser
- [ ] No console errors (check browser DevTools)

## 🧪 Testing

### 1. Quick Test
- [ ] Click "Show Photo Tips" button - tips should appear
- [ ] Click "Choose File" or "Open Camera"
- [ ] Select a food package image
- [ ] Click "Process Image"
- [ ] Wait for results (2-5 seconds)
- [ ] Check if any data was extracted

### 2. API Test (Optional)

In another terminal:
```bash
# Replace with path to your test image
curl -X POST "http://localhost:8000/upload-image" \
  -F "file=@/path/to/food_package.jpg"
```

Expected: JSON response with extracted data

### 3. Health Check
Visit: http://localhost:8000/

Expected: `{"message": "Food Package OCR API is running", "status": "healthy"}`

## ⚠️ Common Issues & Solutions

### Issue: "Import cv2 could not be resolved"
- **When**: Opening project in IDE
- **Solution**: These are just linting warnings. Ignore them or configure Python interpreter in IDE to point to venv.

### Issue: "Tesseract not found"
- **When**: Processing an image
- **Solution**: 
  1. Verify installation: `tesseract --version`
  2. If installed but not found, set path in `ocr_service.py`
  3. If not installed, install Tesseract (see Pre-requisites)

### Issue: CORS errors in browser
- **Symptoms**: "Access to fetch blocked by CORS policy"
- **Solution**: Make sure backend is running on http://localhost:8000

### Issue: Camera not working
- **When**: Click "Open Camera"
- **Solution**:
  1. Grant camera permissions in browser
  2. Use HTTPS or localhost (required by browsers)
  3. Try different browser (Chrome/Firefox recommended)

### Issue: Poor accuracy
- **When**: Text not extracted correctly
- **Solution**:
  1. Read photo tips in the app
  2. Take photo with good lighting, no glare
  3. See `ALGORITHM_DOCUMENTATION.md` for improvement strategies
  4. Consider using advanced processing (see `UPGRADE_GUIDE.md`)

### Issue: Virtual environment not activating (fish shell)
- **Solution**: Use `.fish` extension: `source venv/bin/activate.fish`

## 📚 Next Steps

After basic setup works:

### For Better Accuracy
1. [ ] Read `ALGORITHM_DOCUMENTATION.md` to understand how it works
2. [ ] Try `UPGRADE_GUIDE.md` to switch to advanced processing
3. [ ] Use `QUICK_REFERENCE.md` for troubleshooting

### For Development
1. [ ] Explore API docs at http://localhost:8000/docs
2. [ ] Modify `text_processor.py` to add new extraction patterns
3. [ ] Customize frontend styles in `styles.css`
4. [ ] Add new features per `PROJECT_SUMMARY.md` ideas

### For Understanding
1. [ ] Read through code comments
2. [ ] Try different images to see what works best
3. [ ] Check logs to see processing steps
4. [ ] Experiment with preprocessing parameters

## 🎯 Success Criteria

You're ready to go when:
- [ ] Backend starts without errors
- [ ] Frontend opens in browser
- [ ] Can upload or capture image
- [ ] Gets some results (even if not perfect)
- [ ] No error messages in browser console or terminal

## 📖 Documentation Quick Links

- **Setup help**: `README.md`
- **How it works**: `ALGORITHM_DOCUMENTATION.md`
- **Improve accuracy**: `UPGRADE_GUIDE.md`
- **Quick fixes**: `QUICK_REFERENCE.md`
- **Overview**: `PROJECT_SUMMARY.md`

## 🆘 Still Stuck?

1. Check terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all checklist items above
4. Review the specific documentation file for your issue
5. Check that all files were created correctly

## 🎉 You're Ready!

Once all checklist items are complete, you have a fully functional Food Package OCR Scanner!

Try scanning:
- Cereal boxes
- Snack packages
- Canned foods
- Bottled drinks
- Any food package with printed ingredients/nutrition info

Happy scanning! 🍎
