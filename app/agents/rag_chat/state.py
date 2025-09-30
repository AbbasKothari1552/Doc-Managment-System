from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    query: str
    retrieved_doc_texts: List[str]
    retrieved_sources: List[str]
    response: str
    response_status: str
    messages: Annotated[Sequence[BaseMessage], add_messages]