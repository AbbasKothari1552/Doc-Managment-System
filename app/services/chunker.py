import re
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter


async def chunk(text: str):
    # Normalize Arabic punctuation by inserting line breaks
    text = re.sub(r"([،؛؟])", r"\1\n", text)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,           # Slightly smaller for Arabic (tokens compress differently)
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", "،", "؛", "؟", ""],
        length_function=len
    )
    chunks = await asyncio.to_thread(text_splitter.split_text, text)
    return [c.strip() for c in chunks if c.strip()]