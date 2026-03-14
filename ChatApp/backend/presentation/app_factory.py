import logging
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from application.services.agent_service_impl import AgentServiceImpl
from application.use_cases.create_conversation import CreateConversationUseCase
from application.use_cases.create_project import CreateProjectUseCase
from application.use_cases.delete_conversation import DeleteConversationUseCase
from application.use_cases.delete_project import DeleteProjectUseCase
from application.use_cases.embed_conversation_turn import EmbedConversationTurnUseCase
from application.use_cases.get_conversation_messages import GetConversationMessagesUseCase
from application.use_cases.list_conversations import ListConversationsUseCase
from application.use_cases.list_projects import ListProjectsUseCase
from application.use_cases.list_tools import ListToolsUseCase
from application.use_cases.rename_conversation import RenameConversationUseCase
from application.use_cases.run_agent import RunAgentUseCase
from application.use_cases.search_project_memory import SearchProjectMemoryUseCase
from application.use_cases.update_project import UpdateProjectUseCase
from infrastructure.config import Settings
from infrastructure.database.conversation_repository import ConversationRepository
from infrastructure.database.engine import create_db_engine
from infrastructure.database.project_repository import ProjectRepository
from infrastructure.embedding.gemini_embedding_service import GeminiEmbeddingService
from infrastructure.llm.gemini_service import GeminiLLMService
from infrastructure.tools.calculator import CalculatorTool
from infrastructure.tools.create_note import CreateNoteTool
from infrastructure.tools.get_current_time import GetCurrentTimeTool
from infrastructure.tools.registry import ToolRegistry
from infrastructure.tools.web_search import WebSearchTool
from infrastructure.vector_store.qdrant_vector_store import QdrantVectorStore
from presentation.routes.chat import router as chat_router
from presentation.routes.conversations import router as conversations_router
from presentation.routes.health import router as health_router
from presentation.routes.projects import router as projects_router
from presentation.routes.tools import router as tools_router
from presentation.websocket.chat_ws import websocket_chat

logger = logging.getLogger(__name__)

VECTOR_COLLECTION = "project_memories"
VECTOR_DIMENSION = 768  # Gemini text-embedding-004


def create_app() -> FastAPI:
    settings = Settings()

    # Database
    engine, session_factory = create_db_engine(settings.database_url)
    conversation_repo = ConversationRepository(session_factory)
    project_repo = ProjectRepository(session_factory)

    # Vector store & embedding
    vector_store = QdrantVectorStore(url=settings.qdrant_url)
    embedding_service = GeminiEmbeddingService(
        api_key=settings.gemini_api_key,
        model_name=settings.embedding_model,
    )

    # Tools
    tool_registry = ToolRegistry([
        GetCurrentTimeTool(),
        CalculatorTool(),
        WebSearchTool(),
        CreateNoteTool(),
    ])

    # LLM
    llm_service = GeminiLLMService(
        api_key=settings.gemini_api_key,
        model_name=settings.model_name,
        max_tokens=settings.max_tokens,
        tool_registry=tool_registry,
    )

    # Services & Use Cases
    agent_service = AgentServiceImpl(
        llm_service=llm_service,
        tool_registry=tool_registry,
        max_iterations=settings.max_agent_iterations,
    )
    run_agent_use_case = RunAgentUseCase(agent_service=agent_service)
    list_tools_use_case = ListToolsUseCase(tool_registry=tool_registry)

    # Conversation use cases
    create_conversation_use_case = CreateConversationUseCase(repository=conversation_repo)
    list_conversations_use_case = ListConversationsUseCase(repository=conversation_repo)
    get_conversation_messages_use_case = GetConversationMessagesUseCase(repository=conversation_repo)
    delete_conversation_use_case = DeleteConversationUseCase(repository=conversation_repo)
    rename_conversation_use_case = RenameConversationUseCase(repository=conversation_repo)

    # Project use cases
    create_project_use_case = CreateProjectUseCase(repository=project_repo)
    list_projects_use_case = ListProjectsUseCase(repository=project_repo)
    update_project_use_case = UpdateProjectUseCase(repository=project_repo)
    delete_project_use_case = DeleteProjectUseCase(repository=project_repo, vector_store=vector_store)

    # RAG use cases
    search_memory_use_case = SearchProjectMemoryUseCase(
        embedding_service=embedding_service, vector_store=vector_store,
    )
    embed_turn_use_case = EmbedConversationTurnUseCase(
        embedding_service=embedding_service, vector_store=vector_store,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            await vector_store.ensure_collection(VECTOR_COLLECTION, VECTOR_DIMENSION)
        except Exception:
            logger.warning("Failed to initialize Qdrant collection, RAG will retry lazily", exc_info=True)
        yield
        await vector_store.close()
        await engine.dispose()

    app = FastAPI(title="Agentic AI Chat", lifespan=lifespan)

    # Store on app.state
    app.state.run_agent_use_case = run_agent_use_case
    app.state.list_tools_use_case = list_tools_use_case
    app.state.create_conversation_use_case = create_conversation_use_case
    app.state.list_conversations_use_case = list_conversations_use_case
    app.state.get_conversation_messages_use_case = get_conversation_messages_use_case
    app.state.delete_conversation_use_case = delete_conversation_use_case
    app.state.rename_conversation_use_case = rename_conversation_use_case
    app.state.create_project_use_case = create_project_use_case
    app.state.list_projects_use_case = list_projects_use_case
    app.state.update_project_use_case = update_project_use_case
    app.state.delete_project_use_case = delete_project_use_case

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(tools_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(projects_router)

    @app.websocket("/ws/chat/{conversation_id}")
    async def ws_chat(ws: WebSocket, conversation_id: UUID):
        await websocket_chat(
            ws, run_agent_use_case, conversation_repo, conversation_id,
            search_memory=search_memory_use_case,
            embed_turn=embed_turn_use_case,
        )

    return app
