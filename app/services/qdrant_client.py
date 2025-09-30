import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue, VectorParams

from app.core.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AsyncQdrantManager:
    """Async Qdrant manager with structured pool-like behavior"""
    def __init__(self, **kwargs):
        self.url = settings.QDRANT_URL
        self.api_key = getattr(settings, "QDRANT_API_KEY", None)
        self._client: Optional[AsyncQdrantClient] = None
        self._lock = asyncio.Lock()
        self.collection_name = settings.COLLECTION_NAME


    async def connect(self):
        """Initialize Qdrant connection"""
        async with self._lock:
            if self._client is None:
                try:
                    self._client = AsyncQdrantClient(
                        url=self.url,
                        # api_key=self.api_key
                    )

                    await self._ensure_collection(self.collection_name, settings.VECTOR_SIZE, settings.DISTANCE)
                    logger.info("Qdrant connection established")

                except Exception as e:
                    logger.error(f"Failed to connect to Qdrant: {e}")
                    raise
    
    async def close(self):
        """Close connection (Qdrant client does not really need it but kept for symmetry)"""
        async with self._lock:
            if self._client:
                self._client = None
                logger.info("Qdrant connection closed")

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def _ensure_collection(self, collection_name: str, dim: int, distance):
        """Create collection if missing"""
        collections = await self._client.get_collections()
        if collection_name not in [c.name for c in collections.collections]:
            await self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dim,  # your embedding dimension
                    distance=distance
                )
            )
            logger.info(f"Collection '{collection_name}' created")

    # ------------------ SAVE ------------------
    async def save_embedding(self, embedding: List[float], payload: Dict[str, Any], collection_name=settings.COLLECTION_NAME):
        """Save human/AI conversation"""
        if not self.is_connected:
            await self.connect()


        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload=payload
        )
        await self._client.upsert(collection_name=collection_name, points=[point])
        # logger.info(f"Saved message embedding for user={payload.get('user_id')}, thread={payload.get('thread_id')}")

    # ------------------ SEARCH ------------------
    async def search_embedding(self, embedding: List[float], limit=5, collection_name=settings.COLLECTION_NAME):
        """Retrieve most relevant past messages for a user"""
        if not self.is_connected:
            await self.connect()

        query_vector = embedding  # Assuming `embedding` is already an embedding vector

        results = await self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        return [hit.payload for hit in results]


# Singleton manager
qdrant_manager = AsyncQdrantManager()