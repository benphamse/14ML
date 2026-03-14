# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

An agentic AI chat application with conversation and project management. A Google Gemini-powered agent autonomously uses tools (web search, calculator, time, notes) to answer user questions. Features include persistent chat history, project-scoped conversations, and RAG (Retrieval-Augmented Generation) via Qdrant vector search. Communication happens over WebSocket with real-time streaming of tool steps and text responses.

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
source venv/bin/activate        # activate virtualenv
python main.py                  # starts uvicorn on localhost:8000 with hot reload
pip install -r requirements.txt # install dependencies
```

### Database Migrations (Alembic)
```bash
cd backend
alembic upgrade head            # apply all migrations
alembic revision --autogenerate -m "description"  # create new migration
alembic downgrade -1            # rollback last migration
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

- **Domain** (`domain/`) — Pure Python, no framework imports. Contains entities (dataclasses with factory methods), value objects, and port interfaces (ABCs with `@abstractmethod` in `ports/`).
- **Application** (`application/`) — Use cases (one class per operation), service implementations, and Pydantic DTOs for request/response models.
- **Infrastructure** (`infrastructure/`) — Adapters implementing port interfaces: database repositories (SQLAlchemy), LLM service, embedding service, vector store, tools (extend shared `BaseTool` abstract class), and tool registry.
- **Presentation** (`presentation/`) — Thin HTTP/WS layer. `app_factory.py` wires all DI. REST routes in `routes/`, WebSocket handlers in `websocket/`.

**Entry point**: `main.py` — `from presentation.app_factory import create_app; app = create_app()`

**Database**: PostgreSQL, managed by Alembic migrations. See `infrastructure/database/models.py` for schema.

### Frontend — Clean Architecture Layers (`frontend/`)

- **Domain** (`domain/`) — Pure TypeScript, no Next.js/React imports. Contains entities (extend `BaseEntity<T>` for shared `id`, `equals()`, `clone()`), value objects, and port interfaces.
- **Application** (`application/`) — Use cases (extend `BaseUseCase`), DTOs for API/WS message types. Maps snake_case server responses to domain entities at this boundary.
- **Infrastructure** (`infrastructure/`) — Concrete implementations of port interfaces (WebSocket gateway, HTTP clients).
- **Hooks** (`hooks/`) — Thin bridges between domain layer and React. Each hook composes domain use cases/gateways and exposes React-friendly state + actions.
- **Presentation** (`app/` + `components/`) — Next.js pages and React components. Components handle only rendering and user interaction — no business logic.

### WebSocket Protocol
WebSocket URL: `ws://<host>/ws/chat/{conversation_id}`. On connect, server loads full conversation history from DB.

Client sends `{"type": "message", "content": "..."}` or `{"type": "clear"}`. Server streams back: `tool_call` → `tool_result` (repeated per tool use iteration) → `stream` (text chunks) → `reply` (final response). Error and status messages also possible.

For project-scoped conversations, the server performs RAG search on user input and injects memory snippets into the system prompt. Turns are asynchronously embedded to Qdrant after each response.

### REST API Conventions
- All REST endpoints live under `/api/` prefix
- Resource URLs follow RESTful patterns: `POST /api/{resource}`, `GET /api/{resource}`, `PATCH /api/{resource}/{id}`, `DELETE /api/{resource}/{id}`
- Sub-resources use nesting: `GET /api/{resource}/{id}/{sub-resource}`
- List endpoints support pagination via `limit` and `offset` query params
- All responses use **snake_case** field names
- See route files in `backend/presentation/routes/` for current endpoints

## Key Patterns

- **Interface → Implementation**: Use cases depend only on port interfaces (ABCs), never concrete classes. All DI wiring happens in `app_factory.py`.
- **BaseEntity pattern (FE)**: All frontend entities extend `BaseEntity<T>` for shared `id`, `equals()`, and immutable `clone()` updates (React state compatibility).
- **Sync-to-async bridge**: The Gemini SDK's streaming API is synchronous — it runs in a `ThreadPoolExecutor` and bridges to async via `asyncio.Queue`.
- **Aggregate pattern**: Conversation aggregate encapsulates all history management — adding messages, serializing for LLM, and formatting for JSON.
- **Strategy pattern for notifications**: A `StepNotifier` port abstracts delivery method (WebSocket vs list collection), with concrete implementations selected at runtime.
- **WebSocket routing**: The frontend connects directly to `ws://<host>/ws/chat/{conversationId}` — not proxied through Next.js rewrites (which only cover REST calls).
- **RAG pipeline**: For project-scoped conversations, relevant past turns are retrieved from Qdrant and injected into the system prompt. Turns are asynchronously embedded after each response. RAG failures are non-blocking.
- **Auto-title**: The first user message in a conversation (truncated to 60 chars) automatically becomes the conversation title.

## Docker Infrastructure

All Docker configuration lives in `docker/` at the project root, with each service in its own subfolder containing a Dockerfile and config files. Orchestrated via `docker-compose.yml` at the project root.

### Services
PostgreSQL, Redis, MongoDB, Qdrant, Backend (FastAPI), Frontend (Next.js). Each service has its own subfolder in `docker/` with Dockerfile and config files. All configs are tuned for 100k concurrent users — see individual config files for details.

### Environment
Backend requires a `.env` file in `backend/` with at minimum `GEMINI_API_KEY`, `DATABASE_URL`, `QDRANT_URL`, and `EMBEDDING_MODEL`. For Docker, the compose file reads from `backend/.env` for all service configs.
