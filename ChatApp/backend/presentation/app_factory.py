from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from application.services.agent_service_impl import AgentServiceImpl
from application.use_cases.list_tools import ListToolsUseCase
from application.use_cases.run_agent import RunAgentUseCase
from infrastructure.config import Settings
from infrastructure.llm.gemini_service import GeminiLLMService
from infrastructure.tools.calculator import CalculatorTool
from infrastructure.tools.create_note import CreateNoteTool
from infrastructure.tools.get_current_time import GetCurrentTimeTool
from infrastructure.tools.registry import ToolRegistry
from infrastructure.tools.web_search import WebSearchTool
from presentation.routes.chat import router as chat_router
from presentation.routes.health import router as health_router
from presentation.routes.tools import router as tools_router
from presentation.websocket.chat_ws import websocket_chat


def create_app() -> FastAPI:
    settings = Settings()

    tool_registry = ToolRegistry([
        GetCurrentTimeTool(),
        CalculatorTool(),
        WebSearchTool(),
        CreateNoteTool(),
    ])

    llm_service = GeminiLLMService(
        api_key=settings.gemini_api_key,
        model_name=settings.model_name,
        max_tokens=settings.max_tokens,
        tool_registry=tool_registry,
    )

    agent_service = AgentServiceImpl(
        llm_service=llm_service,
        tool_registry=tool_registry,
        max_iterations=settings.max_agent_iterations,
    )

    run_agent_use_case = RunAgentUseCase(agent_service=agent_service)
    list_tools_use_case = ListToolsUseCase(tool_registry=tool_registry)

    app = FastAPI(title="Agentic AI Chat")

    app.state.run_agent_use_case = run_agent_use_case
    app.state.list_tools_use_case = list_tools_use_case

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

    @app.websocket("/ws/chat")
    async def ws_chat(ws: WebSocket):
        await websocket_chat(ws, run_agent_use_case)

    return app
