import { apiRequest } from "./client";
import type { TokenPair, User } from "../types/models";

type Credentials = {
  email: string;
  password: string;
};

export async function registerUser(payload: Credentials): Promise<User> {
  return apiRequest<User>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload: Credentials): Promise<TokenPair> {
  return apiRequest<TokenPair>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function refreshSession(refreshToken: string): Promise<TokenPair> {
  return apiRequest<TokenPair>("/api/v1/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export async function fetchMe(accessToken: string): Promise<User> {
  return apiRequest<User>("/api/v1/auth/me", { method: "GET" }, accessToken);
}
