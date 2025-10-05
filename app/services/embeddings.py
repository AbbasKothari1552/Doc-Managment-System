import asyncio
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-large")

async def embed_text(text: str, is_query: bool = False):
    """
    Asynchronously generate normalized embeddings using multilingual-e5-large.
    - Automatically adds 'query:' or 'passage:' prefix.
    - Supports both Arabic and English input.
    """
    loop = asyncio.get_event_loop()
    
    # Add the appropriate prefix for E5 models
    prefix = "query: " if is_query else "passage: "
    formatted_text = prefix + text.strip()
    
    # Encode asynchronously to avoid blocking event loop
    embedding = await loop.run_in_executor(
        None,
        lambda: model.encode(
            formatted_text,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
    )
    
    return embedding.tolist()
