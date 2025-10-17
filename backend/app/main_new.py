import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import new simplified routers
from app.routes.agents import router as agents_router
from app.routes.workflows import router as workflows_router
from app.routes.chats import router as chats_router
from app.routes.chat_agent import router as chat_agent_router
from app.utils.new_lifespan import lifespan

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Agentic Engine",
    description="""
    Agentic Engine - A flexible multi-agent platform
    
    This service provides:
    - **Agents**: Create and manage AI agents with custom prompts and workflows
    - **Workflows**: Define reusable workflows/skills that agents can execute
    - **Chats**: Manage chat sessions with agents
    - **Chat Agent**: Send messages to agents and get intelligent responses
    
    ## Features
    - Dynamic agent building with runtime configuration
    - Workflow orchestration
    - Persistent chat history
    - Simple yet powerful API
    """,
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(agents_router, tags=["Agents"])
app.include_router(workflows_router, tags=["Workflows"])
app.include_router(chats_router, tags=["Chats"])
app.include_router(chat_agent_router, tags=["Chat Agent"])


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify the system status.
    """
    logger.info("Received request for health check")
    return {
        "status": "ok",
        "message": "Agentic Engine is healthy and running",
        "version": "2.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Agentic Engine",
        "version": "2.0.0",
        "description": "Multi-agent platform with dynamic workflow orchestration",
        "docs": "/docs",
    }
