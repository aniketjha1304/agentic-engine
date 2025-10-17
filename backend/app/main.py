import logging
import os
from fastapi import FastAPI

# Importing routers
from app.routes.invoke_lisa import router as lisa_router
from app.routes.view_workflow import router as view_workflow_router
from app.routes.deploy_workflow import router as deploy_workflow_router
from app.routes.delete_workflow import router as delete_workflow_router
from app.routes.execute_workflow import router as execute_workflow_router
from app.routes.chat import router as chat_router
from app.routes.lisa_chat import router as lisa_chat_router
from app.routes.lisa_call import router as lisa_call_router
from app.routes.lisa_twilio_call import router as lisa_twilio_call_router
from app.routes.update_workflow_title import router as update_workflow_title_router
from app.routes.stripe_webhook import router as stripe_webhook_router
from app.routes.lisa_chat_websocket import router as lisa_chat_websocket_router
from app.routes.ada_chat_websocket import router as ada_chat_webosocket_router
from app.utils.lifespan import lifespan
from app.utils.ai_brain import azure_ai_search_storage

# azure_ai_search_storage.create_or_update_index()


# search_tool_kit = MSAISearchToolKit(
#     ai_search_base_url=os.getenv("AZURE_AI_SEARCH_BASE_URL"),
#     ai_search_api_key=os.getenv("AZURE_AI_SEARCH_API_KEY"),
#     index_name=os.getenv("LISA_INDEX_NAME"),
#     embeddings_url=os.getenv("EMBEDDINGS_BASE_URL"),
#     embeddings_api_key=os.getenv("EMBEDDINGS_KEY"),
# )

# search_tool_kit.create_memory_storage()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Lisa Engine",
    description="""
    Lisa Engine serves as the interface to connect with Lisa AI. 
    This service offers APIs to invoke Lisa, along with additional functionality for 
    workflow management, including execution, deployment, deletion, and viewing workflows.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(lisa_router, tags=["Lisa"])
app.include_router(view_workflow_router, tags=["View Workflow"])
app.include_router(deploy_workflow_router, tags=["Deploy Workflow"])
app.include_router(execute_workflow_router, tags=["Execute Workflow"])
app.include_router(delete_workflow_router, tags=["Delete Workflow"])
app.include_router(chat_router, tags=["Chats"])
app.include_router(lisa_chat_router, tags=["Lisa Chat"])
app.include_router(lisa_call_router, tags=["Lisa Call"])
app.include_router(lisa_twilio_call_router, tags=["Lisa Twilio Call"])
app.include_router(update_workflow_title_router, tags=["Update Workflow Title"])
app.include_router(lisa_chat_websocket_router, tags=["Lisa chat websocket"])
app.include_router(ada_chat_webosocket_router, tags=["Ada chat websocket"])
app.include_router(stripe_webhook_router, tags=["Stripe webhook"])


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify the system status.
    """
    logger.info("Received request for health check")
    return {"status": "ok", "message": "System is healthy and running."}
