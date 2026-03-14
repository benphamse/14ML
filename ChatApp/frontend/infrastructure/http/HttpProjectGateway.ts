import type { ProjectGateway } from "@/domain/ports/ProjectGateway";
import { ProjectSummary } from "@/domain/entities/ProjectSummary";
import type { ApiProjectResponse, ApiProjectListResponse } from "@/application/dto/project-api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class HttpProjectGateway implements ProjectGateway {
  async listProjects(
    userId: string,
    limit = 50,
    offset = 0,
  ): Promise<ProjectSummary[]> {
    const params = new URLSearchParams({
      user_id: userId,
      limit: String(limit),
      offset: String(offset),
    });
    const res = await fetch(`${API_BASE}/api/projects?${params}`);
    const data: ApiProjectListResponse = await res.json();
    return data.projects.map(ProjectSummary.fromServerData);
  }

  async createProject(
    userId: string,
    name: string,
    description = "",
  ): Promise<ProjectSummary> {
    const params = new URLSearchParams({ user_id: userId });
    const res = await fetch(`${API_BASE}/api/projects?${params}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    const data: ApiProjectResponse = await res.json();
    return ProjectSummary.fromServerData(data);
  }

  async updateProject(
    id: string,
    name?: string,
    description?: string,
  ): Promise<ProjectSummary> {
    const body: Record<string, string> = {};
    if (name !== undefined) body.name = name;
    if (description !== undefined) body.description = description;
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data: ApiProjectResponse = await res.json();
    return ProjectSummary.fromServerData(data);
  }

  async deleteProject(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: "DELETE",
    });
    return res.ok;
  }
}
