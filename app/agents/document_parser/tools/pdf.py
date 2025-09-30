from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from typing import Dict
import os
import time

from langsmith import traceable

# import pytesseract from tesseract_config.py to use configured path
# from app.config.tesseract_config import pytesseract
from app.agents.document_parser.tools.easy_ocr import easyocr_extractor

from app.utils.logger import get_logger
logger = get_logger(__name__)


@traceable(name="PDF Parser")
def extract_pdf_text(input_path: str) -> Dict:
    """Extract text from PDF, with OCR fallback"""
    logger.info(f"Extracting pdf file...")
    try:
        # First try regular extraction
        text = extract_text(input_path)
        
        # If little text found, try OCR
        if len(text.strip()) < 100:
            images = convert_from_path(input_path)
            text = ""
            logger.info("Extracting with EasyOCR...")
            start_time = time.perf_counter()
            
            for image in images:
                text += easyocr_extractor(image) + "\n"
            method = "pdfminer+ocr"

            total_time = time.perf_counter() - start_time
            logger.info(f"OCR processing time: {total_time:.2f} seconds")
        else:
            method = "pdfminer"

        logger.debug(f"Extracted text: {text}")
        
        # # Save extracted text
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     f.write(text)
            
        return {
            "method": method,
            "word_count": len(text.split()),
            "text": text
        }
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")