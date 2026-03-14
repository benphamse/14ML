# Feature Changes

---

## DI Container Refactor (dependency-injector)

**Date:** 2026-03-14

### What Changed

- **`backend/infrastructure/container.py`** *(new)* — `InfraContainer`: all infrastructure singletons (DB engine, session factory, Redis, Qdrant, embedding, tools, LLM).

- **`backend/application/container.py`** *(new)* — `ApplicationContainer`: repos (with cache wrappers) and all use cases, declared as `providers.Singleton` wired from `InfraContainer` via `DependenciesContainer`.

- **`backend/presentation/app_factory.py`** — Reduced from 160 lines to ~90. Now only: wire containers from `Settings`, define lifespan, populate `app.state`, mount routes.

- **`backend/infrastructure/database/engine.py`** — Added `create_engine_from_url` and `create_session_factory_from_engine` as separate composable functions (needed by container providers).

- **`backend/requirements.txt`** — Added `dependency-injector>=4.41.0`.

### Why

As the app scales, manual wiring in one procedural function becomes too long to maintain. `dependency-injector` provides Spring-Boot-style declarative containers — each layer owns its own wiring, and adding a new use case only touches its own container file.

### Structure

```
InfraContainer        (infrastructure/container.py)  — DB, Redis, LLM, Tools
    └─► ApplicationContainer  (application/container.py)   — Repos, Use Cases
            └─► app_factory.py                             — Composes + mounts to FastAPI
```

---

## Redis Caching for Backend Use Cases

**Date:** 2026-03-14

### What Changed

- **`backend/domain/ports/cache_port.py`** *(new)* — `CachePort` ABC defining `get`, `set`, `delete`, `delete_pattern`, `close`.

- **`backend/infrastructure/cache/redis_cache.py`** *(new)* — `RedisCache` implementation using `redis.asyncio`. `delete_pattern` uses `SCAN` cursor loop (safe for production — no `KEYS` command).

- **`backend/infrastructure/repositories/cached_conversation_repository.py`** *(new)* — `CachedConversationRepository` decorator wrapping the real repo. Cache-aside reads with JSON serialization; invalidation on all writes.

- **`backend/infrastructure/repositories/cached_project_repository.py`** *(new)* — `CachedProjectRepository` decorator, same pattern.

- **`backend/infrastructure/config.py`** — Added `redis_url` setting from `REDIS_URL` env var.

- **`backend/requirements.txt`** — Added `redis[hiredis]>=5.0.0`.

- **`backend/presentation/app_factory.py`** — Wires `RedisCache` and wraps both repos with their cached decorators. Closes Redis connection on shutdown.

### Cache Keys & TTLs

| Key pattern | TTL | Invalidated by |
|---|---|---|
| `conv:list:{user_id}:{project_id}:{limit}:{offset}` | 60s | create / rename / delete conversation, add message |
| `conv:{id}` | 120s | rename / delete conversation, add message |
| `conv:msgs:{id}:{limit}:{offset}` | 60s | delete conversation, add message |
| `proj:list:{user_id}:{limit}:{offset}` | 300s | create / update / delete project |
| `proj:{id}` | 300s | update / delete project |

### Why

Redis is provisioned in Docker but was unused by the backend. At 100k concurrent users, all read use cases (list conversations, get messages, list projects) hit PostgreSQL on every request. Caching these with short TTLs dramatically reduces DB load while keeping data fresh.

### Resilience

All cache operations are wrapped in `try/except` — cache failures log a warning and fall through to the real DB. The API never breaks due to Redis being unavailable.
