# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

An agentic AI chat application where a Google Gemini-powered agent can autonomously use tools (web search, calculator, time, notes) to answer user questions. Communication happens over WebSocket with real-time streaming of both tool steps and text responses.

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
source venv/bin/activate        # activate virtualenv
python main.py                  # starts uvicorn on localhost:8000 with hot reload
pip install -r requirements.txt # install dependencies
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install    # install dependencies
pnpm dev        # starts dev server on localhost:3000
pnpm build      # production build
pnpm lint       # run ESLint
```

Both servers must be running simultaneously. The frontend proxies `/api/backend/*` to the backend via Next.js rewrites in `next.config.ts`.

## Design Principles

This project follows **SOLID**, **Clean Architecture**, **OOP**, **DDD**, and **DRY** across both frontend and backend.

### Production-Ready for 100k Users
All code and configuration must be **production-ready for 100,000 concurrent users**. This applies to every layer:

**Backend:**
- Database queries must use proper indexes — no full table scans. Always add indexes for columns used in WHERE, ORDER BY, and JOIN clauses.
- Use connection pooling (SQLAlchemy async pool with bounded `pool_size` and `max_overflow`). Never create connections per-request.
- All I/O operations must be async (`await`). Never block the event loop with synchronous calls.
- Use pagination for all list endpoints — never return unbounded result sets.
- Implement proper error handling with structured error responses — no unhandled exceptions leaking to clients.
- WebSocket connections must handle backpressure and graceful disconnection.
- Use bulk operations (batch inserts/updates) when processing multiple records.
- Cache frequently-read, rarely-changed data via Redis.
- Log with structured logging (JSON) at appropriate levels — no `print()` statements.

**Frontend:**
- Virtualize long lists (conversations, messages) — never render 10,000+ DOM nodes.
- Debounce user input that triggers API calls (search, typing indicators).
- Use optimistic UI updates where safe, with rollback on failure.
- Lazy-load routes and heavy components. Minimize initial bundle size.
- Handle loading, error, and empty states for every async operation.

**Infrastructure / Docker:**
- All services must have health checks, resource limits, and restart policies.
- Database configs must be tuned for the target scale (connection limits, memory, WAL settings).
- Use multi-stage Docker builds to minimize image size.
- Secrets must come from environment variables — never hardcoded.

**General:**
- No N+1 queries. Use eager loading or batch fetching for related data.
- Validate and sanitize all external input at system boundaries.
- Design schemas and APIs for horizontal scalability — stateless services, externalized sessions.

### API Convention
- All API response fields use **snake_case** (e.g. `tool_steps`, `current_time`, `created_at`).
- Frontend models may use camelCase internally but must map to/from snake_case at the API boundary.

### Prefer External Libraries
- **Use well-maintained external libraries (5,000+ GitHub stars) over manual implementations** when a proven solution exists.
- Before writing custom logic for common tasks (HTTP clients, validation, date handling, state management, etc.), search for a popular library that solves it.
- This applies to both backend (PyPI) and frontend (npm). Prioritize libraries that are actively maintained, well-documented, and widely adopted.

### DRY Code
- **Do not repeat yourself.** When two or more classes share common logic, extract it into a shared abstraction rather than duplicating.
- Before writing new code, check if the logic already exists elsewhere. Prefer extending or composing existing abstractions over creating parallel implementations.
- A shared abstraction is justified when 2+ classes share the same logic. Do not pre-abstract for hypothetical reuse.

### Interfaces & OOP (Inheritance, Abstract Classes, Polymorphism)
Use a layered OOP approach: **interface → abstract class → concrete class**.

**Backend (Python):**
- Define contracts as **ABCs** (`abc.ABC`) with `@abstractmethod` in `domain/ports/`. These are the interfaces.
- When 2+ implementations share common logic, create an **intermediate abstract class** that implements the ABC and provides shared behavior. Concrete classes inherit from this. Example:
  - `Tool` (ABC in `domain/ports/`) → `BaseTool(Tool)` (abstract, shared `format_response()`, `validate_args()`) → `CalculatorTool(BaseTool)`, `WebSearchTool(BaseTool)`
  - `StepNotifier` (ABC) → `BaseNotifier(StepNotifier)` (shared serialization) → `WsStepNotifier`, `ListStepNotifier`
- Use `@property` + `@abstractmethod` for attributes that subclasses must define (e.g. `name`, `description`).
- Prefer **composition over inheritance** when classes don't share an "is-a" relationship. Use inheritance only for genuine type hierarchies.

**Frontend (TypeScript):**
- Define contracts as **interfaces** in `domain/ports/` (e.g. `ChatGateway`).
- When 2+ classes share common behavior, create an **abstract class** implementing the interface with shared logic. Concrete classes extend it. Example:
  - `ChatGateway` (interface) → `BaseGateway` (abstract, shared reconnect/send logic) → `WebSocketChatGateway`
  - `UseCase<TInput, TOutput>` (interface) → `BaseUseCase<TInput, TOutput>` (abstract, shared gateway ref) → `SendMessageUseCase`, `ClearChatUseCase`
- Use `implements` for interfaces, `extends` for abstract/base classes.
- Domain entities: use abstract classes when entities share immutable-update patterns or factory method signatures.

### Adding a New Tool
Create a new class in `backend/infrastructure/tools/` implementing the `Tool` ABC from `domain/ports/tool_port.py`, then register it in `presentation/app_factory.py` inside `create_app()`. No existing code needs to be modified (OCP).

## Architecture

### Backend — Clean Architecture Layers (`backend/`)

**Domain** (`domain/`) — Pure Python, no framework imports:
- `entities/message.py` — `Message` dataclass with factory methods (`Message.user()`, `Message.assistant()`)
- `entities/conversation.py` — `Conversation` aggregate managing message list, history serialization, and LLM history formatting
- `entities/tool_result.py` — `ToolResult` frozen dataclass (value object)
- `ports/tool_port.py` — `Tool` ABC interface (name, description, parameters properties + async execute)
- `ports/llm_port.py` — `LLMService` ABC interface (create_chat, stream_message)
- `ports/step_notifier_port.py` — `StepNotifier` ABC interface (notify)
- `ports/agent_service_port.py` — `AgentService` ABC interface (run)
- `ports/tool_registry_port.py` — `ToolRegistryPort` ABC interface (get_tool, list_all)

**Application** (`application/`) — Use cases + service implementations:
- `use_cases/run_agent.py` — `RunAgentUseCase` — thin orchestrator delegating to `AgentService` interface
- `use_cases/list_tools.py` — `ListToolsUseCase` — depends on `ToolRegistryPort` interface
- `services/agent_service_impl.py` — `AgentServiceImpl` implements `AgentService`. Contains the agentic loop: stream from LLM, execute tools, feed results back. Depends on `LLMService` + `ToolRegistryPort` interfaces.
- `dto/chat_dto.py` — Pydantic `ChatRequest`/`ChatResponse` models
- `dto/ws_messages.py` — Pydantic models for all WebSocket message types

**Infrastructure** (`infrastructure/`) — Adapters implementing ports:
- `llm/gemini_service.py` — `GeminiLLMService` implements `LLMService`. Bridges Gemini's sync streaming to async via `ThreadPoolExecutor` + `asyncio.Queue`. Handles 429 retry logic.
- `tools/base_tool.py` — `BaseTool(Tool)` abstract class with shared attribute-based properties (`_name`, `_description`, `_parameters`) and `format_success()`/`format_error()` helpers
- `tools/` — Each tool (`GetCurrentTimeTool`, `CalculatorTool`, `WebSearchTool`, `CreateNoteTool`) extends `BaseTool`
- `tools/registry.py` — `ToolRegistry` implements `ToolRegistryPort`. Holds tools, provides `get_tool(name)`, `get_gemini_tools()`, `list_all()`
- `config.py` — `Settings` frozen dataclass loading from `.env`

**Presentation** (`presentation/`) — Thin HTTP/WS layer:
- `app_factory.py` — `create_app()` wires all DI: Settings → tools → registry → LLM service → AgentServiceImpl → use cases → routes
- `routes/health.py`, `routes/chat.py`, `routes/tools.py` — FastAPI routers. Access use cases via `request.app.state`
- `websocket/chat_ws.py` — WebSocket handler using `Conversation` aggregate + `RunAgentUseCase`
- `websocket/ws_step_notifier.py` — `BaseNotifier(StepNotifier)` abstract with shared `serialize()`, then `WsStepNotifier` and `ListStepNotifier`

**Entry point**: `main.py` — just `from presentation.app_factory import create_app; app = create_app()`

### Frontend — Clean Architecture Layers (`frontend/`)

**Domain** (`domain/`) — Pure TypeScript, no React:
- `entities/BaseEntity.ts` — Abstract base class providing shared `id`, `equals()`, protected `clone()` pattern, and `generateId()` static helper. All entities extend this.
- `entities/Message.ts` — `Message extends BaseEntity<Message>` with immutable update via `clone()` (`withContent`, `withAppendedContent`, `withToolStep`, `withToolSteps`) and factory methods (`createUser`, `createAssistantPlaceholder`)
- `entities/ToolStep.ts` — `ToolStep` value object class with `displayName` getter and `fromServerData` factory
- `entities/Conversation.ts` — `Conversation extends BaseEntity<Conversation>` aggregate managing `Message[]` immutably via `clone()` (`addUserMessage`, `updateLastAssistant`, `clear`)
- `ports/ChatGateway.ts` — Interface for WebSocket communication

**Application** (`application/`):
- `use-cases/BaseUseCase.ts` — `UseCase<TInput, TOutput>` interface + `BaseUseCase` abstract class with shared `gateway` constructor injection
- `use-cases/SendMessageUseCase.ts` — `extends BaseUseCase<string, void>`, delegates to gateway
- `use-cases/ClearChatUseCase.ts` — `extends BaseUseCase`, delegates to gateway
- `dto/ws-messages.ts` — TypeScript types for all WS protocol messages (snake_case from server)

**Infrastructure** (`infrastructure/`):
- `websocket/WebSocketChatGateway.ts` — Implements `ChatGateway`. Handles connect, auto-reconnect (3s), send, message/connection callbacks.

**Hooks** (`hooks/`) — Thin bridges between domain and React:
- `useChat.ts` — Instantiates gateway + use cases, manages `Conversation` state, wires WS message handler to update conversation. Exposes `messages`, `isLoading`, `isConnected`, `sendMessage`, `clearChat`.
- `useAutoScroll.ts` — Scroll-to-bottom sentinel ref

**Presentation** (`app/` + `components/`):
- `app/page.tsx` — Thin shell (~55 lines) using `useChat` + `useAutoScroll`, renders components
- `components/ChatMessage.tsx` — Markdown rendering + typewriter animation
- `components/ChatInput.tsx` — Auto-resizing textarea
- `components/Header.tsx` — Connection status + clear button
- `components/ToolStep.tsx` — Expandable tool call/result visualization

### WebSocket Protocol
Client sends `{"type": "message", "content": "..."}` or `{"type": "clear"}`. Server streams back: `tool_call` → `tool_result` (repeated per tool use iteration) → `stream` (text chunks) → `reply` (final response). Error and status messages also possible.

## Key Patterns

- **Interface → Implementation**: Backend services are defined as ABC interfaces in `domain/ports/` and implemented in `application/services/` or `infrastructure/`. Use cases depend only on interfaces, never concrete classes. DI wiring happens in `app_factory.py`.
- **BaseEntity pattern (FE)**: `Message` and `Conversation` extend `BaseEntity<T>`, sharing `id`, `equals()`, and `clone()`. Immutable updates return new instances via `clone()` for React state compatibility.
- The Gemini SDK's streaming API is synchronous. `GeminiLLMService` runs it in a `ThreadPoolExecutor` and bridges to async via `asyncio.Queue`.
- `Conversation` aggregate encapsulates all history management — adding messages, serializing for LLM, and formatting for JSON.
- `StepNotifier` port abstracts how tool steps are delivered: `WsStepNotifier` sends over WebSocket, `ListStepNotifier` collects into a list (for the REST endpoint).
- The frontend connects directly to `ws://localhost:8000/ws/chat` (not proxied through Next.js rewrites, which only cover REST calls).

## Docker Infrastructure

All Docker configuration lives in `docker/` at the project root, with each service in its own subfolder containing a Dockerfile and config files. Orchestrated via `docker-compose.yml` at the project root.

### Services (tuned for 100k users)
- **PostgreSQL 16** (`docker/postgres/`) — Primary relational DB with custom `postgresql.conf` (200 connections, tuned buffers) and `init.sql` (uuid-ossp, pgcrypto, pg_trgm extensions)
- **Redis 7** (`docker/redis/`) — Caching, sessions, rate limiting. AOF persistence, 256MB memory with LRU eviction
- **MongoDB 7** (`docker/mongodb/`) — NoSQL for analytics, logs, flexible documents
- **Qdrant** (`docker/qdrant/`) — Vector DB for embeddings and semantic search
- **Backend** (`docker/backend/`) — FastAPI app with 4 uvicorn workers
- **Frontend** (`docker/frontend/`) — Multi-stage Next.js build (deps → build → standalone runner)

### Commands
```bash
docker compose up -d              # start all services
docker compose up -d postgres redis  # start only infra services (for local dev)
docker compose down               # stop all
docker compose logs -f backend    # tail backend logs
```

### Environment
Copy `.env.example` at project root and fill in values. The compose file reads from this `.env` for all service credentials and ports.

## Environment Setup
Backend requires a `.env` file in `backend/` with at minimum `GEMINI_API_KEY`. See `backend/.env.example`. For Docker, use the root `.env.example` which includes all service configs.
