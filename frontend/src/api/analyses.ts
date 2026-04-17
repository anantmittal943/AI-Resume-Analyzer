import { apiRequest } from "./client";
import type { Analysis, HistoryPage } from "../types/models";

export async function createAnalysis(
  accessToken: string,
  resumeId: string,
  jobId: string,
): Promise<Analysis> {
  return apiRequest<Analysis>(
    "/api/v1/analyses",
    {
      method: "POST",
      body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
    },
    accessToken,
  );
}

export async function getAnalysisHistory(
  accessToken: string,
  limit = 10,
  offset = 0,
): Promise<HistoryPage> {
  return apiRequest<HistoryPage>(
    `/api/v1/analyses/history?limit=${limit}&offset=${offset}`,
    { method: "GET" },
    accessToken,
  );
}
