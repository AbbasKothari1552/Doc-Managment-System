from langchain_core.tools import tool

from app.services.embeddings import embed_text
from app.services.qdrant_client import qdrant_manager

@tool
async def vector_search(query: str) -> list:
    """Tool to perform vector search in the document embeddings."""
    try:
        query_embedding = await embed_text(query)

        results = await qdrant_manager.search_embedding(query_embedding)

        # Implement vector search logic here
        return results
    except Exception as e:
        return f"Error occurred during vector search: {e}"