import type { ProjectGateway } from "@/domain/ports/ProjectGateway";
import { ProjectSummary } from "@/domain/entities/ProjectSummary";
import type { ApiProjectResponse, ApiProjectListResponse } from "@/application/dto/project-api";
import apiClient from "./apiClient";

export class HttpProjectGateway implements ProjectGateway {
  async listProjects(userId: string, limit = 50, offset = 0): Promise<ProjectSummary[]> {
    const { data } = await apiClient.get<ApiProjectListResponse>("/api/projects", {
      params: { user_id: userId, limit, offset },
    });
    return data.projects.map(ProjectSummary.fromServerData);
  }

  async createProject(userId: string, name: string, description = ""): Promise<ProjectSummary> {
    const { data } = await apiClient.post<ApiProjectResponse>(
      "/api/projects",
      { name, description },
      { params: { user_id: userId } },
    );
    return ProjectSummary.fromServerData(data);
  }

  async updateProject(id: string, name?: string, description?: string): Promise<ProjectSummary> {
    const { data } = await apiClient.patch<ApiProjectResponse>(
      `/api/projects/${id}`,
      { ...(name !== undefined && { name }), ...(description !== undefined && { description }) },
    );
    return ProjectSummary.fromServerData(data);
  }

  async deleteProject(id: string): Promise<boolean> {
    await apiClient.delete(`/api/projects/${id}`);
    return true;
  }
}
