import os
import json
import asyncio

from langchain_core.messages import SystemMessage, HumanMessage

from app.core.settings import settings
from app.agents.document_parser.state import State
from app.agents.document_parser.tools import (
    extract_docx_text, 
    extract_excel_text, 
    extract_image_text, 
    extract_pdf_text
    )

from app.utils.logger import get_logger
logger = get_logger(__name__)

# Helper function
def get_extractor(filepath: str):
        """Get appropriate extractor based on file type"""
        logger.info(f"Getting extractor for file: {filepath}")

        # Split the path into root and extension
        _, ext = os.path.splitext(filepath)
        file_type = ext[1:].lower() if ext else ''  # Remove the dot and convert to lower case

        if file_type == "pdf":
            return extract_pdf_text
        elif file_type in ["doc", "docx"]:
            return extract_docx_text
        elif file_type in ["xls", "xlsx"]:
            return extract_excel_text
        elif file_type in ["jpg", "jpeg", "png", "tiff"]:
            return extract_image_text
        return None


async def save_file_node(state: State) -> State:
    """Node to save uploaded file and update state with file path."""
    logger.info("Starting Save File Node.")

    upload_file = state.get("upload_file")
    if not upload_file:
        logger.warning("No file provided in state.")
        state["file_save_status"] = "failed"
        return state

    try:
        from app.utils.file_handler import save_file  # Import here to avoid circular dependency
        result = await save_file(upload_file)
        state["file_path"] = result.get("file_path")
        state["original_filename"] = result.get("original_filename")
        state["file_save_status"] = "success"

        logger.info(f"File saved successfully: {state['file_path']}")
        return state

    except Exception as e:
        logger.error(f"File saving failed: {str(e)}")
        state["file_save_status"] = "failed"
        return state


async def parser_agent(state: State) -> State:
        """Main extraction method"""
        logger.info(f"Starting Parser Agent.")

        # get file path
        file_path = state.get("file_path")

        # get extractor 
        extractor = get_extractor(file_path)
        if not extractor:
            logger.warning(f"No extractor available for file: {file_path}")
            state["extraction_status"] = "failed"
            return state
        
        try:
            result = await asyncio.to_thread(
                extractor,
                input_path=file_path
            )

            # Update the existing state object instead of returning a new one
            state["doc_text"] = result.get("text")
            state["extraction_method"] = result.get("method")
            state["extraction_status"] = "success"

            logger.info(f"Extraction completed for file: {file_path}")

            return state

        except Exception as e:
            logger.error(f"Extraction failed for {file_path}: {str(e)}")

            state["extraction_status"] = "failed"
            return state
        

async def chunking_node(state: State) -> State:
    """Chunk extracted document text for further processing."""
    logger.info("Starting Chunking Node.")

    doc_text = state.get("doc_text")
    if not doc_text:
        logger.warning("No document text available for chunking.")
        state["chunking_status"] = "failed"
        return state

    try:
        from app.services.chunker import chunk  # Import here to avoid circular dependency

        chunks = await chunk(doc_text)
        state["doc_chunks"] = chunks
        state["chunking_status"] = "success"

        logger.info(f"Chunking completed. Total chunks created: {len(chunks)}")
        return state

    except Exception as e:
        logger.error(f"Chunking failed: {str(e)}")
        state["chunking_status"] = "failed"
        return state
    
async def embedding_node(state: State) -> State:
    """Node to create embeddings for document chunks."""
    logger.info("Starting Embedding Node.")

    doc_chunks = state.get("doc_chunks")
    if not doc_chunks:
        logger.warning("No document chunks available for embedding.")
        state["embedding_status"] = "failed"
        return state

    try:
        from app.services.embeddings import embed_text  # Import here to avoid circular dependency

        # Create embeddings for each chunk asynchronously
        embeddings = await asyncio.gather(*(embed_text(chunk) for chunk in doc_chunks))
        state["doc_embeddings"] = embeddings
        state["embedding_status"] = "success"

        logger.info(f"Embedding completed. Total embeddings created: {len(embeddings)}")
        return state

    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        state["embedding_status"] = "failed"
        return state
    
async def store_embeddings_node(state: State) -> State:
    """Node to store document embeddings in Qdrant."""
    logger.info("Starting Store Embeddings Node.")

    doc_embeddings = state.get("doc_embeddings")
    doc_chunks = state.get("doc_chunks")
    file_path = state.get("file_path")
    file_category = state.get("predicted_category")
    original_filename = state.get("original_filename")

    if not doc_embeddings or not doc_chunks:
        logger.warning("No embeddings or chunks available for storage.")
        state["storage_status"] = "failed"
        return state

    if len(doc_embeddings) != len(doc_chunks):
        logger.error("Mismatch between number of embeddings and chunks.")
        state["storage_status"] = "failed"
        return state

    try:
        from app.services.qdrant_client import qdrant_manager

        # Prepare payloads and save each embedding with its corresponding chunk
        for idx, (embedding, chunk) in enumerate(zip(doc_embeddings, doc_chunks)):
            payload = {
                "file_category": file_category,
                "file_path": file_path,
                "original_filename": original_filename,
                "chunk_index": idx,
                "chunk_text": chunk
            }
            await qdrant_manager.save_embedding(embedding=embedding, payload=payload)
            logger.debug(f"Stored embedding for chunk {idx}")

        state["storage_status"] = "success"
        logger.info(f"All embeddings stored successfully for file: {file_path}")
        return state

    except Exception as e:
        logger.error(f"Storing embeddings failed: {str(e)}")
        state["storage_status"] = "failed"
        return state
        
async def predict_category_node(state: State) -> State:
    """Node to predict document category using LLM."""
    logger.info("Starting Predict Category Node.")

    doc_text = state.get("doc_text")
    trimmed_text = doc_text if len(doc_text) <= 5000 else doc_text[:5000]
    if not trimmed_text:
        logger.warning("No document text available for category prediction.")
        state["category_prediction_status"] = "failed"
        return state

    try:
        from app.utils.helpers import get_chat_model  # Import here to avoid circular dependency

        model = get_chat_model()

        system_prompt = f"""
        You are a document classifier. Given the document content, return only the most appropriate category name from the following list:

        {', '.join(settings.CATEGORY_LIST)}

        Return ONLY the category name. Do not include any explanation, formatting, or additional words.

        Example Output:
        Technical

        Document content:

        {trimmed_text}
        """
        messages = [
            SystemMessage(content=system_prompt),
        ]

        try:
            # call LLM
            response = await model.ainvoke(messages)
        except Exception as e:
            logger.error(f"Error in doc_analyzer_node LLM call: {e}")

        category = response.content.strip()

        state["predicted_category"] = category
        state["category_prediction_status"] = "success"

        logger.info(f"Category prediction completed: {category}")
        return state

    except Exception as e:
        logger.error(f"Category prediction failed: {str(e)}")
        state["category_prediction_status"] = "failed"
        return state