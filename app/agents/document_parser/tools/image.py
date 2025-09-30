from PIL import Image
from typing import Dict
from pathlib import Path
import time

from app.utils.logger import get_logger
logger = get_logger(__name__)

from langsmith import traceable

# import pytesseract from tesseract_config.py to use configured path
# from app.config.tesseract_config import pytesseract
from app.agents.document_parser.tools.easy_ocr import easyocr_extractor

@traceable(name="Image Parser")
def extract_image_text(input_path: str) -> Dict:
    """Extract text from image using OCR"""
    logger.info(f"Extracting image file...")
    try:
        start_time = time.perf_counter()

        text = easyocr_extractor(input_path)

        total_time = time.perf_counter() - start_time
        logger.debug(f"OCR processing time: {total_time:.2f} seconds")
        
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     f.write(text)
        
        return {
            "content_type": "ocr_text",
            "method": "easyocr",
            "word_count": len(text.split()),
            "text": text
        }
    except Exception as e:
        raise Exception(f"OCR failed: {str(e)}")