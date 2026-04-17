export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
};

export type Resume = {
  id: string;
  filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
};

export type Job = {
  id: string;
  title: string;
  company: string | null;
  description: string;
  created_at: string;
};

export type KeywordMatch = {
  keyword: string;
  matched: boolean;
};

export type Analysis = {
  id: string;
  resume_id: string;
  job_id: string;
  suitability_score: number;
  summary: string;
  strengths: string[];
  gaps: string[];
  keyword_breakdown: KeywordMatch[];
  provider_used: string;
  created_at: string;
};

export type HistoryPage = {
  total: number;
  limit: number;
  offset: number;
  items: Analysis[];
};
