from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from langgraph.checkpoint.memory import MemorySaver

from app.agents.rag_chat.graph import rag_chat_graph

from app.utils.logger import get_logger
logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/chat")
async def chat_answer(
    request:Request,
    chatrequest: ChatRequest,
):

    """Handle chat requests."""
    logger.info("Received chat request.")
    

    # static for now
    thread_id = "upload"

    config = {"configurable": {"thread_id": str(thread_id)}}

    memory = MemorySaver() 

    initial_state = {
        "query": chatrequest.query,
    }

    graph = await rag_chat_graph(checkpointer=memory)

    response = await graph.ainvoke(
        initial_state,
        config=config,
    )  

    # Extract content properly
    answer = response.get("response", "")

    # If you also attach references, include them here
    references = response.get("references", [])

    return JSONResponse(content={
        "answer": answer,
        "references": references
    })