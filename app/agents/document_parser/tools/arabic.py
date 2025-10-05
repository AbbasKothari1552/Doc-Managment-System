import pytesseract
from pdf2image import convert_from_path
import os
import sys

# Set the path to the tesseract executable (only needed if it's not in your system's PATH)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_arabic_with_tesseract(input_path: str):
    images = convert_from_path(input_path, dpi=300)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="ara") + "\n"
    return {
            "method": "ocr",
            "word_count": len(text.split()),
            "text": text
        }
