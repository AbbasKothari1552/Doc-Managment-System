from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client.http.models import Distance


from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    BASE_URL: str

    GROQ_API_KEY: str

    # QDrant Vector DB settings
    QDRANT_URL: str
    QDRANT_API_KEY: str = ""
    COLLECTION_NAME: str = "documents_test"
    VECTOR_SIZE: int = 1024
    DISTANCE: Distance = Distance.COSINE

    # LLM Models
    QWEN_LLM: str = "qwen/qwen3-32b"
    OPENAI_GPT_120: str = "openai/gpt-oss-120b"
    OPENAI_GPT_20: str = "openai/gpt-oss-20b"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Models settings 
    TEMPERATURE: float = 0.7

    # logging settings
    DEBUG: bool = False
    LOG_LEVEL: str = "DEBUG"
    LOG_DIR: Path  = Path("logs")

    # Langsmith settings
    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING: str 
    LANGSMITH_ENDPOINT: str 
    LANGSMITH_PROJECT: str 

    # Easyocr Languages list
    EASYOCR_LANGUAGES: list = ['en']

    # Document settings
    DATA_DIR: Path = Path("data/docs")

    # category list
    CATEGORY_LIST: list = [
        "HR",
        "Finance",
        "Legal",
        "Operations",
        "Marketing",
        "Technical",
        "Educational",
        "Personal",
        "Business",
        "Government",
        "Other"
    ]


settings = Settings()