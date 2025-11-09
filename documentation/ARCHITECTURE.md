# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Browser - Frontend)                        │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Camera     │  │  File Upload │  │    Display   │          │
│  │   Capture    │  │              │  │    Results   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────▲───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                   │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │ HTTP POST /upload-image
                             │ (multipart/form-data)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API SERVER                           │
│                     (FastAPI - Python)                           │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      main.py                               │  │
│  │  - Receives image                                          │  │
│  │  - Validates input                                         │  │
│  │  - Orchestrates processing                                 │  │
│  │  - Returns JSON response                                   │  │
│  └───────────────────┬───────────────────────────────────────┘  │
│                      │                                            │
│         ┌────────────┼────────────┐                              │
│         ▼            ▼            ▼                              │
│  ┌────────────┐ ┌─────────┐ ┌───────────┐                      │
│  │   Image    │ │   OCR   │ │   Text    │                      │
│  │  Processor │ │ Service │ │ Processor │                      │
│  └────────────┘ └─────────┘ └───────────┘                      │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Detailed Component Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. IMAGE INPUT                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Camera Capture          File Upload                                │
│   ┌─────────────┐        ┌─────────────┐                           │
│   │ getUserMedia│        │  <input>    │                           │
│   │   API       │        │ type="file" │                           │
│   └──────┬──────┘        └──────┬──────┘                           │
│          │                      │                                    │
│          │   Canvas Capture     │  File Read                        │
│          ▼                      ▼                                    │
│   ┌────────────────────────────────┐                               │
│   │         Blob Object            │                               │
│   │    (JPEG/PNG image data)       │                               │
│   └────────────┬───────────────────┘                               │
│                │                                                     │
│                │ FormData POST                                      │
│                ▼                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 2. BACKEND RECEPTION & VALIDATION                                   │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   ┌────────────────────────┐                                       │
│   │  FastAPI Endpoint      │                                       │
│   │  /upload-image         │                                       │
│   └────────────┬───────────┘                                       │
│                │                                                     │
│                │ Validate                                           │
│                ├─► Content-Type: image/*                           │
│                ├─► File size reasonable                            │
│                └─► Not corrupted                                   │
│                │                                                     │
│                │ Convert to numpy array                            │
│                ▼                                                     │
│   ┌────────────────────────┐                                       │
│   │  OpenCV Image Object   │                                       │
│   │  (numpy array, BGR)    │                                       │
│   └────────────┬───────────┘                                       │
│                │                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 3. IMAGE PREPROCESSING (image_processor.py)                         │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   Step 1: Resize                                                    │
│   ┌──────────────────────────────────────┐                         │
│   │  Target: ~1500px width               │                         │
│   │  Method: Cubic interpolation         │                         │
│   │  Maintains aspect ratio              │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 2: Grayscale                                                 │
│   ┌──────────────────────────────────────┐                         │
│   │  BGR → Gray (1 channel)              │                         │
│   │  Reduces computational load          │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 3: Denoise                                                   │
│   ┌──────────────────────────────────────┐                         │
│   │  Non-local Means Denoising           │                         │
│   │  Smooths noise, preserves edges      │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 4: CLAHE (Contrast Enhancement)                              │
│   ┌──────────────────────────────────────┐                         │
│   │  Adaptive histogram equalization     │                         │
│   │  8x8 tiles, clipLimit=2.0            │                         │
│   │  Handles uneven lighting             │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 5: Adaptive Threshold                                        │
│   ┌──────────────────────────────────────┐                         │
│   │  Gaussian adaptive threshold          │                         │
│   │  Block size: 11x11                   │                         │
│   │  Binarize: text=white, bg=black      │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 6: Morphological Clean                                       │
│   ┌──────────────────────────────────────┐                         │
│   │  Close: Fill holes in characters     │                         │
│   │  Open: Remove small noise            │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│                  ▼                                                   │
│   ┌────────────────────────────────────┐                           │
│   │  Preprocessed Binary Image         │                           │
│   │  (Black text on white bg)          │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 4. OCR TEXT EXTRACTION (ocr_service.py)                             │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   ┌────────────────────────────────────┐                           │
│   │   Tesseract OCR Engine             │                           │
│   │   Config: --oem 3 --psm 6 -l eng   │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
│   ┌────────────▼───────────────────────┐                           │
│   │  Layout Analysis                   │                           │
│   │  - Find text regions               │                           │
│   │  - Segment into lines/words        │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
│   ┌────────────▼───────────────────────┐                           │
│   │  Character Recognition             │                           │
│   │  - LSTM neural network             │                           │
│   │  - Language model (English)        │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
│                ▼                                                     │
│   ┌────────────────────────────────────┐                           │
│   │  Raw Text String                   │                           │
│   │  "Ingredients: flour, sugar..."    │                           │
│   │  "Calories: 250 kcal"              │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 5. TEXT POST-PROCESSING (text_processor.py)                         │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   Step 1: Clean Text                                                │
│   ┌──────────────────────────────────────┐                         │
│   │  Remove excessive whitespace         │                         │
│   │  Remove special characters           │                         │
│   │  Normalize format                    │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 2: Extract Calories                                          │
│   ┌──────────────────────────────────────┐                         │
│   │  Regex: r'calories?\s*:?\s*(\d+)'   │                         │
│   │  Also: "energy", "kcal", etc.       │                         │
│   │  Result: {"value": 250, "unit": ...}│                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 3: Extract Serving Size                                      │
│   ┌──────────────────────────────────────┐                         │
│   │  Regex: r'serving\s+size\s*:?\s*...' │                         │
│   │  Result: {"value": "100g", ...}     │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 4: Extract Ingredients                                       │
│   ┌──────────────────────────────────────┐                         │
│   │  Find "Ingredients:" section         │                         │
│   │  Split by commas/semicolons          │                         │
│   │  Result: {"list": [...], ...}       │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 5: Extract Nutrition Facts                                   │
│   ┌──────────────────────────────────────┐                         │
│   │  Search for: protein, fat, carbs...  │                         │
│   │  Extract numeric values + units      │                         │
│   │  Result: {"protein": {val, unit}...} │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Step 6: Extract Allergens                                         │
│   ┌──────────────────────────────────────┐                         │
│   │  Search for common allergens         │                         │
│   │  Result: {"list": ["milk", ...]}    │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│                  ▼                                                   │
│   ┌────────────────────────────────────┐                           │
│   │     Structured Data Object         │                           │
│   │  {calories, serving, ingredients,  │                           │
│   │   nutrition_facts, allergens}      │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 6. JSON RESPONSE                                                     │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   ┌────────────────────────────────────┐                           │
│   │  FastAPI JSONResponse              │                           │
│   │  {                                 │                           │
│   │    "success": true,                │                           │
│   │    "message": "...",               │                           │
│   │    "data": {...},                  │                           │
│   │    "raw_text": "..."               │                           │
│   │  }                                 │                           │
│   └────────────┬───────────────────────┘                           │
│                │                                                     │
│                │ HTTP 200                                           │
│                ▼                                                     │
└────────────────┼───────────────────────────────────────────────────┘
                 │
┌────────────────┼───────────────────────────────────────────────────┐
│ 7. FRONTEND DISPLAY (app.js)                                        │
├────────────────┼───────────────────────────────────────────────────┤
│                ▼                                                     │
│   Parse JSON Response                                               │
│   ┌──────────────────────────────────────┐                         │
│   │  Extract each data field             │                         │
│   │  Check if found/valid                │                         │
│   └──────────────┬───────────────────────┘                         │
│                  │                                                   │
│   Render Results                                                    │
│   ┌──────────────────────────────────────┐                         │
│   │  Calories Card                       │                         │
│   │  Serving Size Card                   │                         │
│   │  Ingredients List                    │                         │
│   │  Nutrition Table                     │                         │
│   │  Allergens List                      │                         │
│   │  Raw JSON (collapsible)              │                         │
│   └──────────────────────────────────────┘                         │
│                                                                       │
│   User sees formatted results ✓                                    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Data Flow Timing

```
User Action               Time        Component
─────────────────────────────────────────────────────────────
Click "Process"           0ms         Frontend
  │
  ├─► Upload to server    100ms       Network
  │
  ├─► Validate image      50ms        main.py
  │
  ├─► Preprocess          500ms       image_processor.py
  │     ├─ Resize         100ms
  │     ├─ Grayscale      50ms
  │     ├─ Denoise        200ms
  │     ├─ CLAHE          100ms
  │     └─ Threshold      50ms
  │
  ├─► OCR Extraction      1000ms      ocr_service.py
  │     ├─ Layout         200ms
  │     └─ Recognition    800ms
  │
  ├─► Post-process        100ms       text_processor.py
  │     ├─ Calories       20ms
  │     ├─ Serving        20ms
  │     ├─ Ingredients    30ms
  │     └─ Nutrients      30ms
  │
  ├─► Build response      50ms        main.py
  │
  └─► Send to client      100ms       Network
                          ────────
Total:                    ~2000ms

Display results           50ms        Frontend
─────────────────────────────────────────────────────────────
Total User Wait Time:     ~2 seconds
```

## Component Dependencies

```
main.py
├─► image_processor.py
│   └─► cv2 (OpenCV)
│   └─► numpy
│
├─► ocr_service.py
│   └─► pytesseract
│   └─► PIL (Pillow)
│
└─► text_processor.py
    └─► re (regex)
    └─► typing

Frontend (app.js)
└─► No dependencies (vanilla JS)
```

## Error Handling Flow

```
┌─────────────┐
│   Error     │
│  Detected   │
└──────┬──────┘
       │
       ├─► Invalid Image?
       │   └─► Return 400: "File must be an image"
       │
       ├─► Corrupt Image?
       │   └─► Return 400: "Invalid image file"
       │
       ├─► Processing Error?
       │   ├─► Log error with traceback
       │   └─► Return 500: "Error processing image"
       │
       └─► No Text Found?
           └─► Return 200: {success: false, message: "No text detected"}

Frontend receives error:
├─► Show error section
├─► Display user-friendly message
└─► Offer "Try Again" button
```

## Advanced Processing Path (Optional)

```
Standard Path:              Advanced Path:
─────────────              ────────────────

Image                       Image
  │                           │
  ├─► Basic Preprocess        ├─► Multiple Preprocessing Methods
  │                           │   ├─ Shiny optimized
  │                           │   ├─ Standard
  │                           │   ├─ High contrast
  │                           │   ├─ Inverted
  │                           │   └─ Multiple thresholds
  │                           │
  ├─► Single OCR Pass         ├─► Multi-Pass OCR
  │   (PSM 6)                 │   ├─ Try PSM 3, 4, 6, 11, 12
  │                           │   ├─ Calculate confidence for each
  │                           │   └─ Pick best result
  │                           │
  │                           ├─► Image Quality Check
  │                           │   ├─ Brightness check
  │                           │   ├─ Blur detection
  │                           │   ├─ Contrast analysis
  │                           │   └─ Resolution check
  │                           │
  └─► Text Extraction         └─► Text Extraction

Time: ~2s                    Time: ~5-8s
Accuracy: 70%                Accuracy: 85%
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
├─────────────────────────────────────────────────────────┤
│  HTML5  │  CSS3   │  JavaScript ES6+  │  Camera API    │
└─────────────────────────────────────────────────────────┘
                           │
                    HTTP/REST API
                           │
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
├─────────────────────────────────────────────────────────┤
│              FastAPI (Python 3.8+)                      │
│    - Routing  - Validation  - Error Handling            │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
┌─────────────▼──┐  ┌──────▼──────┐  ┌─▼─────────────┐
│   PROCESSING   │  │     OCR     │  │   PARSING     │
│     LAYER      │  │    LAYER    │  │    LAYER      │
├────────────────┤  ├─────────────┤  ├───────────────┤
│   OpenCV       │  │ Pytesseract │  │  Python re    │
│   - Resize     │  │ - LSTM      │  │  - Regex      │
│   - Filter     │  │ - Layout    │  │  - Extract    │
│   - Threshold  │  │ - Recognize │  │  - Structure  │
└────────────────┘  └─────────────┘  └───────────────┘
        │                   │               │
        │                   │               │
┌───────▼───────────────────▼───────────────▼───────────┐
│                   LIBRARY LAYER                        │
├────────────────────────────────────────────────────────┤
│  NumPy  │  Pillow  │  Uvicorn  │  Python Standard Lib │
└────────────────────────────────────────────────────────┘
```

## File Relationships

```
Project Root
│
├─ Documentation Files (Markdown)
│  ├─ README.md ──────────────────► Entry point, setup guide
│  ├─ GETTING_STARTED.md ─────────► Step-by-step checklist
│  ├─ ALGORITHM_DOCUMENTATION.md ─► Deep technical details
│  ├─ UPGRADE_GUIDE.md ───────────► How to improve accuracy
│  ├─ QUICK_REFERENCE.md ─────────► Problem-solution matrix
│  ├─ PROJECT_SUMMARY.md ─────────► Overview and comparison
│  └─ ARCHITECTURE.md (this file) ► System design
│
├─ backend/
│  ├─ main.py ────────────────────► Entry point, orchestration
│  │    │
│  │    ├─imports─► image_processor.py ─► Preprocessing
│  │    ├─imports─► ocr_service.py ─────► OCR
│  │    └─imports─► text_processor.py ──► Parsing
│  │
│  ├─ image_processor_advanced.py ► Enhanced preprocessing
│  ├─ ocr_service_advanced.py ────► Multi-pass OCR
│  ├─ requirements.txt ───────────► Dependencies
│  └─ .gitignore
│
└─ frontend/
   ├─ index.html ─────────────────► UI structure
   ├─ styles.css ─────────────────► Styling
   └─ app.js ─────────────────────► Logic & API calls
       │
       └─calls─► http://localhost:8000/upload-image
```

## Deployment Options

```
Development:
┌──────────────┐      ┌──────────────┐
│   Browser    │◄────►│  localhost   │
│ (Frontend)   │      │  :8000       │
│ File System  │      │  (Backend)   │
└──────────────┘      └──────────────┘

Production Option 1 (Simple):
┌──────────────┐      ┌──────────────┐
│   Browser    │◄────►│  VPS Server  │
│              │      │  - Nginx     │
│              │      │  - Uvicorn   │
└──────────────┘      └──────────────┘

Production Option 2 (Container):
┌──────────────┐      ┌──────────────┐
│   Browser    │◄────►│   Docker     │
│              │      │  - Frontend  │
│              │      │  - Backend   │
└──────────────┘      └──────────────┘

Production Option 3 (Cloud):
┌──────────────┐      ┌──────────────┐
│   Browser    │◄────►│  Cloud Run   │
│              │      │  Google Cloud│
│              │      │  Azure       │
└──────────────┘      └──────────────┘
```

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Modular components (easy to swap/upgrade)
- ✅ Testable units
- ✅ Scalable design
- ✅ Documented flow
