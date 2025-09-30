import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter


async def chunk(text:str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = await asyncio.to_thread(text_splitter.split_text, text)
    return chunks