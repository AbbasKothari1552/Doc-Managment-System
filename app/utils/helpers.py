from langchain_groq import ChatGroq

from app.core.settings import settings

from app.utils.logger import get_logger
logger = get_logger(__name__)

def get_chat_model() -> ChatGroq:
    """Return a ChatGroq model instance."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.OPENAI_GPT_120,
        temperature=settings.TEMPERATURE,
    )