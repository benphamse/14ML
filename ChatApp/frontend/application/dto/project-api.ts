export interface ApiProjectResponse {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ApiProjectListResponse {
  projects: ApiProjectResponse[];
}
