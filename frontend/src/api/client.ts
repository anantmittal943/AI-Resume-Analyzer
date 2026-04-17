import type { TokenPair } from "../types/models";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const STORAGE_KEY = "ai_resume_tokens";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const tokenStorage = {
  get(): TokenPair | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as TokenPair;
    } catch {
      return null;
    }
  },
  set(tokens: TokenPair): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
  },
  clear(): void {
    localStorage.removeItem(STORAGE_KEY);
  },
};

async function doRequest<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Ignore JSON parse failures for non-JSON responses.
    }
    throw new ApiError(response.status, message);
  }
  return (await response.json()) as T;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  accessToken?: string,
): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  return doRequest<T>(path, {
    ...init,
    headers,
  });
}
