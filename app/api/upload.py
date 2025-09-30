from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Body
from fastapi import Request
from typing import List, Dict

from langgraph.checkpoint.memory import MemorySaver

from app.agents.document_parser.graph import document_parser_graph

from app.utils.logger import get_logger
logger = get_logger(__name__)


router = APIRouter()

@router.post("/upload", response_model=Dict)
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...),
):
    """
    Upload files and process them through the pipeline:
    1. File upload and metadata creation
    2. Content extraction
    3. Text chunking
    4. Embedding generation
    """

    logger.info(f"Received upload request with {len(files)} files")

    # static for now
    thread_id = "upload"

    config = {"configurable": {"thread_id": str(thread_id)}}

    memory = MemorySaver()

    results = []
    for file in files:
        try:

            try:
                from app.utils.file_handler import save_file  # Import here to avoid circular dependency
                result = await save_file(file)
                file_path = result.get("file_path")
                original_filename = result.get("original_filename")
            except Exception as e:
                logger.error(f"Failed to read file {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": f"File read error: {str(e)}"
                })
                continue

            initial_state = {
                "file_path": file_path,
                "original_filename": original_filename,
            }

            graph = await document_parser_graph(checkpointer=memory)

            response = await graph.ainvoke(
                initial_state,
                config=config,
            )

            results.append({
                    "filename": response.get("original_filename"),
                    "status": "success",
                })

        except Exception as e:
            logger.error(f"Failed to initialize state for file {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": f"State initialization error: {str(e)}"
            })
            continue

    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Upload processed",
            # "results": results,
            # "successful": [r for r in results if r["status"] == "success"],
            # "failed": [r for r in results if r["status"] == "failed"],
        }
    )