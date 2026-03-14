import type { ProjectSummary } from "@/domain/entities/ProjectSummary";

export interface ProjectGateway {
  listProjects(userId: string, limit?: number, offset?: number): Promise<ProjectSummary[]>;
  createProject(userId: string, name: string, description?: string): Promise<ProjectSummary>;
  updateProject(id: string, name?: string, description?: string): Promise<ProjectSummary>;
  deleteProject(id: string): Promise<boolean>;
}
