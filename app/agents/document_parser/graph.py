from langgraph.graph import END, START, StateGraph

from app.agents.document_parser.nodes import (
    save_file_node,
    parser_agent,
    chunking_node,
    embedding_node,
    store_embeddings_node,
    predict_category_node
)

from app.agents.document_parser.state import State

from app.utils.logger import get_logger
logger = get_logger(__name__)

async def document_parser_graph(checkpointer) -> StateGraph:

    graph_builder = StateGraph(State)

    # Add all nodes
    # graph_builder.add_node("SaveFileNode", save_file_node)
    graph_builder.add_node("ParserNode", parser_agent)
    graph_builder.add_node("ChunkingNode", chunking_node)
    graph_builder.add_node("EmbeddingNode", embedding_node)
    graph_builder.add_node("CategoryPredictionNode", predict_category_node)
    graph_builder.add_node("StoreEmbeddingsNode", store_embeddings_node)

    # Define workflow
    # graph_builder.add_edge(START, "SaveFileNode")
    graph_builder.add_edge(START, "ParserNode")
    graph_builder.add_edge("ParserNode", "ChunkingNode")
    graph_builder.add_edge("ChunkingNode", "EmbeddingNode")
    graph_builder.add_edge("EmbeddingNode", "CategoryPredictionNode")
    graph_builder.add_edge("CategoryPredictionNode", "StoreEmbeddingsNode")
    graph_builder.add_edge("StoreEmbeddingsNode", END)

    return graph_builder.compile(
        name="DocumentParserGraph",
        checkpointer=checkpointer
    )