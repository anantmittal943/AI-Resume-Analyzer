import { apiRequest } from "./client";
import type { Resume } from "../types/models";

export async function listResumes(accessToken: string): Promise<Resume[]> {
  return apiRequest<Resume[]>("/api/v1/resumes", { method: "GET" }, accessToken);
}

export async function uploadResume(accessToken: string, file: File): Promise<Resume> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<Resume>(
    "/api/v1/resumes",
    {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    },
  );
}
