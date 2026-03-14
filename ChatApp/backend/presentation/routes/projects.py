from uuid import UUID

from fastapi import APIRouter, Request, HTTPException

from application.dto.project_dto import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter(prefix="/api/projects")


def _to_response(project) -> ProjectResponse:
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    request: Request,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
):
    use_case = request.app.state.list_projects_use_case
    projects = await use_case.execute(user_id, limit, offset)
    return ProjectListResponse(projects=[_to_response(p) for p in projects])


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: Request,
    user_id: str,
    body: CreateProjectRequest,
):
    use_case = request.app.state.create_project_use_case
    project = await use_case.execute(user_id, body.name, body.description)
    return _to_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    request: Request,
    project_id: UUID,
    body: UpdateProjectRequest,
):
    use_case = request.app.state.update_project_use_case
    project = await use_case.execute(project_id, body.name, body.description)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_response(project)


@router.delete("/{project_id}")
async def delete_project(
    request: Request,
    project_id: UUID,
):
    use_case = request.app.state.delete_project_use_case
    deleted = await use_case.execute(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}
