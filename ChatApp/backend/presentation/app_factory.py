import logging
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from application.container import ApplicationContainer
from infrastructure.config import Settings
from infrastructure.container import InfraContainer
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

    # ── Wire containers ────────────────────────────────────────────────────
    infra = InfraContainer()
    infra.config.from_dict({
        "database_url": settings.database_url,
        "redis_url": settings.redis_url,
        "qdrant_url": settings.qdrant_url,
        "gemini_api_key": settings.gemini_api_key,
        "model_name": settings.model_name,
        "max_tokens": settings.max_tokens,
        "max_agent_iterations": settings.max_agent_iterations,
        "embedding_model": settings.embedding_model,
    })
    app_container = ApplicationContainer(infra=infra)

    # ── Lifespan ───────────────────────────────────────────────────────────
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            await infra.vector_store().ensure_collection(VECTOR_COLLECTION, VECTOR_DIMENSION)
        except Exception:
            logger.warning("Failed to initialize Qdrant collection, RAG will retry lazily", exc_info=True)
        yield
        await infra.redis_cache().close()
        await infra.vector_store().close()
        await infra.db_engine().dispose()

    # ── App setup ──────────────────────────────────────────────────────────
    app = FastAPI(title="Agentic AI Chat", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Store use cases on app.state ───────────────────────────────────────
    app.state.run_agent_use_case = app_container.run_agent()
    app.state.list_tools_use_case = app_container.list_tools()
    app.state.create_conversation_use_case = app_container.create_conversation()
    app.state.list_conversations_use_case = app_container.list_conversations()
    app.state.get_conversation_messages_use_case = app_container.get_conversation_messages()
    app.state.delete_conversation_use_case = app_container.delete_conversation()
    app.state.rename_conversation_use_case = app_container.rename_conversation()
    app.state.create_project_use_case = app_container.create_project()
    app.state.list_projects_use_case = app_container.list_projects()
    app.state.update_project_use_case = app_container.update_project()
    app.state.delete_project_use_case = app_container.delete_project()

    # ── Routes ─────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(tools_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(projects_router)

    @app.websocket("/ws/chat/{conversation_id}")
    async def ws_chat(ws: WebSocket, conversation_id: UUID):
        await websocket_chat(
            ws, app_container.run_agent(), app_container.conversation_repo(),
            conversation_id,
            search_memory=app_container.search_memory(),
            embed_turn=app_container.embed_turn(),
        )

    return app
