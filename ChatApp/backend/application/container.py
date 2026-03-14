from dependency_injector import containers, providers

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
from infrastructure.repositories.cached_conversation_repository import CachedConversationRepository
from infrastructure.repositories.cached_project_repository import CachedProjectRepository
from infrastructure.repositories.conversation_repository import ConversationRepository
from infrastructure.repositories.project_repository import ProjectRepository


class ApplicationContainer(containers.DeclarativeContainer):
    infra = providers.DependenciesContainer()

    # ── Repositories ──────────────────────────────────────────────────────
    conversation_repo = providers.Singleton(
        CachedConversationRepository,
        repo=providers.Singleton(ConversationRepository, session_factory=infra.session_factory),
        cache=infra.redis_cache,
    )
    project_repo = providers.Singleton(
        CachedProjectRepository,
        repo=providers.Singleton(ProjectRepository, session_factory=infra.session_factory),
        cache=infra.redis_cache,
    )

    # ── Agent ──────────────────────────────────────────────────────────────
    agent_service = providers.Singleton(
        AgentServiceImpl,
        llm_service=infra.llm_service,
        tool_registry=infra.tool_registry,
        max_iterations=infra.config.max_agent_iterations.as_int(),
    )
    run_agent = providers.Singleton(RunAgentUseCase, agent_service=agent_service)
    list_tools = providers.Singleton(ListToolsUseCase, tool_registry=infra.tool_registry)

    # ── Conversation use cases ─────────────────────────────────────────────
    create_conversation = providers.Singleton(CreateConversationUseCase, repository=conversation_repo)
    list_conversations = providers.Singleton(ListConversationsUseCase, repository=conversation_repo)
    get_conversation_messages = providers.Singleton(GetConversationMessagesUseCase, repository=conversation_repo)
    delete_conversation = providers.Singleton(DeleteConversationUseCase, repository=conversation_repo)
    rename_conversation = providers.Singleton(RenameConversationUseCase, repository=conversation_repo)

    # ── Project use cases ──────────────────────────────────────────────────
    create_project = providers.Singleton(CreateProjectUseCase, repository=project_repo)
    list_projects = providers.Singleton(ListProjectsUseCase, repository=project_repo)
    update_project = providers.Singleton(UpdateProjectUseCase, repository=project_repo)
    delete_project = providers.Singleton(
        DeleteProjectUseCase, repository=project_repo, vector_store=infra.vector_store,
    )

    # ── RAG use cases ──────────────────────────────────────────────────────
    search_memory = providers.Singleton(
        SearchProjectMemoryUseCase,
        embedding_service=infra.embedding_service,
        vector_store=infra.vector_store,
    )
    embed_turn = providers.Singleton(
        EmbedConversationTurnUseCase,
        embedding_service=infra.embedding_service,
        vector_store=infra.vector_store,
    )
