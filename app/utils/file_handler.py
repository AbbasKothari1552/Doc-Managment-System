import os
import aiofiles
import uuid
from fastapi import UploadFile, HTTPException

from app.core.settings import settings


async def save_file(file: UploadFile, folder: str = settings.DATA_DIR) -> str:
    """
    Save an uploaded file asynchronously and return the saved path.
    Generates a unique filename to avoid collisions.

    Args:
        file (UploadFile): The uploaded file object.
        folder (str): Directory to save the file. Default: 'data'.

    Returns:
        str: Path where file is saved.
    """

    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    # Extract extension
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    # if ext not in ALLOWED_EXTENSIONS:
    #     raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Unique filename (UUID)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(folder, unique_name)

    # Save file asynchronously
    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await out_file.write(chunk)

    return {
        "file_path": file_path,
        "original_filename": file.filename,
    }
