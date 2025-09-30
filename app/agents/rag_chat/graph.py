from langgraph.graph import END, START, StateGraph

from app.agents.rag_chat.nodes import (
    rag_assistant_node
)

from app.agents.rag_chat.state import State

from app.utils.logger import get_logger
logger = get_logger(__name__)

async def rag_chat_graph(checkpointer) -> StateGraph:

    graph_builder = StateGraph(State)

    # Add all nodes
    graph_builder.add_node("RAGAssistantNode", rag_assistant_node)

    # Define workflow
    graph_builder.add_edge(START, "RAGAssistantNode")
    graph_builder.add_edge("RAGAssistantNode", END)

    return graph_builder.compile(
        name="RAGChatGraph",
        checkpointer=checkpointer
    )