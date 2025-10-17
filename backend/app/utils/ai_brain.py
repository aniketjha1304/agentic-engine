# Configure the brain_with_embedding
import os
from dotenv import load_dotenv
from cognitive_space.brain import Brain
from cognitive_space.storage import AzureAISearchStorage
from cognitive_space.algorithms.embedding_model import EmbeddingEncode
from cognitive_space.algorithms.embedding_model import EmbeddingRecall
from cognitive_space.tool_builder.cognitive_encoder_tool import (
    build_standard_encoder_tool,
)
from cognitive_space.tool_builder.cognitive_recall_tool import (
    build_standard_recall_tool,
)
from app.config.env import (
    LISA_INDEX_NAME,
    EMBEDDINGS_KEY,
    EMBEDDINGS_BASE_URL,
    AZURE_AI_SEARCH_BASE_URL,
    AZURE_AI_SEARCH_API_KEY,
)

load_dotenv()


azure_ai_search_storage = AzureAISearchStorage(
    endpoint=AZURE_AI_SEARCH_BASE_URL,
    api_key=AZURE_AI_SEARCH_API_KEY,
    index_name=LISA_INDEX_NAME,
)
embedding_encode = EmbeddingEncode(
    storage_layer=azure_ai_search_storage,
    base_url=EMBEDDINGS_BASE_URL,
    api_key=EMBEDDINGS_KEY,
)

embedding_recall = EmbeddingRecall(
    storage_layer=azure_ai_search_storage,
    base_url=EMBEDDINGS_BASE_URL,
    api_key=EMBEDDINGS_KEY,
)
brain_with_embeddings = Brain(
    cognitive_encoder=embedding_encode, cognitive_recall=embedding_recall
)

encoder_tool = build_standard_encoder_tool(brain_with_embeddings)
recaller_tool = build_standard_recall_tool(brain_with_embeddings)
