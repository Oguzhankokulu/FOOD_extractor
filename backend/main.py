from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
from PIL import Image
import io
import logging

from image_processor import ImageProcessor
from ocr_service import OCRService
from text_processor import TextProcessor
from barcode_service import BarcodeService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Food Package OCR API", version="1.0.0")

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_processor = ImageProcessor()
ocr_service = OCRService()
text_processor = TextProcessor()
barcode_service = BarcodeService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Food Package OCR API is running", "status": "healthy"}


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image of a food package and extract ingredients and calorie information.
    First tries barcode scanning with OpenFoodFacts Turkey API, then falls back to OCR.
    
    Args:
        file: Image file (jpg, png, etc.)
    
    Returns:
        JSON containing extracted ingredients and nutritional information
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        logger.info(f"Processing image: {file.filename}")
        
        # Read image file
        contents = await file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Step 1: Try barcode scanning first
        logger.info("Attempting barcode detection...")
        barcode_data = barcode_service.scan_and_fetch(image)
        
        if barcode_data:
            logger.info("Product found via barcode!")
            return JSONResponse(content={
                "success": True,
                "message": "Product found via barcode from OpenFoodFacts",
                "method": "barcode",
                "data": barcode_data
            })
        
        # Step 2: No barcode found, fall back to OCR
        logger.info("No barcode found, falling back to OCR...")
        
        # Step 2a: Preprocess image
        logger.info("Preprocessing image...")
        processed_image = image_processor.preprocess(image)
        
        # Step 2b: Perform OCR with Turkish + English
        logger.info("Performing OCR (Turkish + English)...")
        raw_text = ocr_service.extract_text(processed_image)
        
        if not raw_text.strip():
            return JSONResponse(content={
                "success": False,
                "message": "No barcode found and no text detected in image",
                "method": "ocr",
                "data": None
            })
        
        # Step 2c: Post-process and extract structured data
        logger.info("Extracting structured data from OCR...")
        structured_data = text_processor.extract_food_data(raw_text)
        structured_data["source"] = "ocr"
        
        logger.info("OCR processing complete")
        return JSONResponse(content={
            "success": True,
            "message": "Image processed successfully via OCR",
            "method": "ocr",
            "data": structured_data,
            "raw_text": raw_text[:500]  # Include first 500 chars of raw text for debugging
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
