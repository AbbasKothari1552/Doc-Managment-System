import os
import json
import asyncio

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from app.core.settings import settings
from app.agents.rag_chat.state import State
from app.agents.rag_chat.tools import vector_search
from app.utils.helpers import get_chat_model
from app.agents.rag_chat.prompts import SYSTEM_PROMPT

from app.utils.logger import get_logger
logger = get_logger(__name__)

async def rag_assistant_node(state: State) -> State:
    """Node to handle RAG chat assistant logic."""
    logger.info("Starting RAG Chat Assistant Node.")

    query = state.get("query")
    if not query:
        logger.warning("No query provided in state.")
        state["response_status"] = "failed"
        return state

    try:
        model = get_chat_model()
        # Define tools
        tools = [vector_search]
        # Create ReAct agent
        react_agent = create_react_agent(model, tools=tools)

        system_prompt = SYSTEM_PROMPT

        # Build message sequence
        messages = [
            SystemMessage(content=system_prompt),
            *state["messages"],  # previous conversation (history)
            HumanMessage(content=state.get("query"))
        ]

        response = await react_agent.ainvoke({
            "messages": messages
        })

        if response:
            content = response["messages"][-1].content
            state['response'] = content
            # Create new messages to append
            new_human_message = HumanMessage(content=state["query"])
            new_ai_message = AIMessage(content=state["response"])
            state["response_status"] = "success"
            return {
                **state, 
                'messages': [new_human_message, new_ai_message]
            }
        else:
            state["response_status"] = "failed"
            return state

    except Exception as e:
        pass