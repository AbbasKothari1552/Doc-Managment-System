from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
from app.services.qdrant_client import qdrant_manager

from app.api import (
    upload_router,
    chat_router
)

from app.utils.logger import get_logger
logger = get_logger(__name__)

BASE_URL = "http://localhost:8000"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    
    # Startup
    try:
        # Initialize Qdrant connection
        await qdrant_manager.connect()

        logger.info("Application started successfully")
        yield
        
    finally:     
        # Close qdrant database pool
        await qdrant_manager.close()
        
        print("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

# Setup Jinja2 template rendering
templates = Jinja2Templates(directory="app/templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/files", tags=["files"])
app.include_router(chat_router, prefix="/api")

# upload files html page
@app.get("/upload", response_class=HTMLResponse)
def read_root(request: Request):
    print("Templates:", templates)
    return templates.TemplateResponse("upload_files.html", {"request": request, "base_url": BASE_URL})

# Rag chat html page
@app.get("/rag_chat", response_class=HTMLResponse)
def rag_chat(request: Request):
    print("Templates:", templates)
    return templates.TemplateResponse("rag_chat.html", {"request": request, "base_url": BASE_URL})