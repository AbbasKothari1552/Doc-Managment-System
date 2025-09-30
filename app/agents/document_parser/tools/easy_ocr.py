from typing import Dict, Union
from easyocr import Reader
import numpy as np
from PIL import Image
from langsmith import traceable

from app.core.settings import settings
from app.utils.logger import get_logger
logger = get_logger(__name__)

reader = Reader(settings.EASYOCR_LANGUAGES, gpu=False)  # Initialize once, use CPU

@traceable(name="Easy OCR Parser")
def easyocr_extractor(image: Union[str, Image.Image, np.ndarray]) -> str:
    """Extract text from image file path, PIL image, or numpy array using EasyOCR"""
    logger.info("Starting EasyOCR extraction...")
    try:
        if isinstance(image, Image.Image):
            # Convert PIL Image to numpy array
            image = np.array(image)

        result = reader.readtext(image, detail=0)  # returns list of strings
        text = "\n".join(result)
        return text.strip()
    
    except Exception as e:
        raise Exception(f"EasyOCR failed: {str(e)}")
