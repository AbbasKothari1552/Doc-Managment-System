from .docs import extract_docx_text
from .excel import extract_excel_text
from .image import extract_image_text
from .pdf import extract_pdf_text 
from .easy_ocr import easyocr_extractor

__all__ = [
    "extract_docx_text",
    "extract_excel_text",
    "extract_image_text",
    "extract_pdf_text",
    "easyocr_extractor"
]