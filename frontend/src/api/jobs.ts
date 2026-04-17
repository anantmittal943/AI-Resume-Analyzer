import { apiRequest } from "./client";
import type { Job } from "../types/models";

type JobPayload = {
  title: string;
  company?: string;
  description: string;
};

export async function listJobs(accessToken: string): Promise<Job[]> {
  return apiRequest<Job[]>("/api/v1/jobs", { method: "GET" }, accessToken);
}

export async function createJob(accessToken: string, payload: JobPayload): Promise<Job> {
  return apiRequest<Job>(
    "/api/v1/jobs",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    accessToken,
  );
}
