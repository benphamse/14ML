import { useState, useRef, useEffect, useCallback } from "react";

import { ProjectSummary } from "@/domain/entities/ProjectSummary";
import { HttpProjectGateway } from "@/infrastructure/http/HttpProjectGateway";

const USER_ID = "default";

export function useProjectList() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const gatewayRef = useRef(new HttpProjectGateway());

  const loadProjects = useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await gatewayRef.current.listProjects(USER_ID);
      setProjects(list);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const createProject = useCallback(async (name: string, description = ""): Promise<ProjectSummary> => {
    const created = await gatewayRef.current.createProject(USER_ID, name, description);
    setProjects((prev) => [created, ...prev]);
    return created;
  }, []);

  const deleteProject = useCallback(async (id: string) => {
    await gatewayRef.current.deleteProject(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
  }, []);

  const updateProject = useCallback(async (id: string, name?: string, description?: string) => {
    const updated = await gatewayRef.current.updateProject(id, name, description);
    setProjects((prev) => prev.map((p) => (p.id === id ? updated : p)));
  }, []);

  return {
    projects,
    isLoading,
    createProject,
    deleteProject,
    updateProject,
    refreshList: loadProjects,
  };
}
