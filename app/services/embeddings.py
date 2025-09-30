import asyncio
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")
# # Save it locally wherever you want
# model.save("models/all-MiniLM-L6-v2")


async def embed_text(text: str):
    # Wrap in asyncio to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: model.encode(text).tolist())