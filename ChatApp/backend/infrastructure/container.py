from dependency_injector import containers, providers

from infrastructure.cache.redis_cache import RedisCache
from infrastructure.database.engine import create_engine_from_url, create_session_factory_from_engine
from infrastructure.embedding.gemini_embedding_service import GeminiEmbeddingService
from infrastructure.llm.gemini_service import GeminiLLMService
from infrastructure.tools.calculator import CalculatorTool
from infrastructure.tools.create_note import CreateNoteTool
from infrastructure.tools.get_current_time import GetCurrentTimeTool
from infrastructure.tools.registry import ToolRegistry
from infrastructure.tools.web_search import WebSearchTool
from infrastructure.vector_store.qdrant_vector_store import QdrantVectorStore


class InfraContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database
    db_engine = providers.Singleton(create_engine_from_url, database_url=config.database_url)
    session_factory = providers.Singleton(create_session_factory_from_engine, engine=db_engine)

    # Cache
    redis_cache = providers.Singleton(RedisCache, url=config.redis_url)

    # Vector store & embedding
    vector_store = providers.Singleton(QdrantVectorStore, url=config.qdrant_url)
    embedding_service = providers.Singleton(
        GeminiEmbeddingService,
        api_key=config.gemini_api_key,
        model_name=config.embedding_model,
    )

    # Tools
    tool_registry = providers.Singleton(
        ToolRegistry,
        tools=providers.List(
            providers.Factory(GetCurrentTimeTool),
            providers.Factory(CalculatorTool),
            providers.Factory(WebSearchTool),
            providers.Factory(CreateNoteTool),
        ),
    )

    # LLM
    llm_service = providers.Singleton(
        GeminiLLMService,
        api_key=config.gemini_api_key,
        model_name=config.model_name,
        max_tokens=config.max_tokens.as_int(),
        tool_registry=tool_registry,
    )
