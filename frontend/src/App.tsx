import { FormEvent, useEffect, useMemo, useState } from "react";

import { createAnalysis, getAnalysisHistory } from "./api/analyses";
import { fetchMe, refreshSession } from "./api/auth";
import { ApiError, tokenStorage } from "./api/client";
import { createJob, listJobs } from "./api/jobs";
import { listResumes, uploadResume } from "./api/resumes";
import AuthPanel from "./components/AuthPanel";
import HistoryPanel from "./components/HistoryPanel";
import type { Analysis, Job, Resume, TokenPair, User } from "./types/models";


export default function App() {
  const [tokens, setTokens] = useState<TokenPair | null>(() => tokenStorage.get());
  const [user, setUser] = useState<User | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [history, setHistory] = useState<Analysis[]>([]);
  const [latestAnalysis, setLatestAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobCompany, setJobCompany] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const hasDataToAnalyze = useMemo(
    () => resumes.length > 0 && jobs.length > 0,
    [resumes.length, jobs.length],
  );

  async function runWithRefresh<T>(operation: (accessToken: string) => Promise<T>): Promise<T> {
    if (!tokens) {
      throw new Error("Not authenticated");
    }

    try {
      return await operation(tokens.access_token);
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401 &&
        tokens.refresh_token
      ) {
        const refreshed = await refreshSession(tokens.refresh_token);
        tokenStorage.set(refreshed);
        setTokens(refreshed);
        return operation(refreshed.access_token);
      }
      throw error;
    }
  }

  async function loadDashboardData() {
    if (!tokens) {
      return;
    }
    setLoading(true);
    setErrorMessage(null);

    try {
      const me = await runWithRefresh((token) => fetchMe(token));
      const [resumeItems, jobItems, historyPage] = await Promise.all([
        runWithRefresh((token) => listResumes(token)),
        runWithRefresh((token) => listJobs(token)),
        runWithRefresh((token) => getAnalysisHistory(token, 10, 0)),
      ]);
      setUser(me);
      setResumes(resumeItems);
      setJobs(jobItems);
      setHistory(historyPage.items);
      if (historyPage.items.length > 0) {
        setLatestAnalysis(historyPage.items[0]);
      }
      if (!selectedResumeId && resumeItems.length > 0) {
        setSelectedResumeId(resumeItems[0].id);
      }
      if (!selectedJobId && jobItems.length > 0) {
        setSelectedJobId(jobItems[0].id);
      }
    } catch (error) {
      tokenStorage.clear();
      setTokens(null);
      setUser(null);
      setErrorMessage(error instanceof Error ? error.message : "Unable to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!tokens) {
      return;
    }
    void loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tokens?.access_token]);

  async function handleResumeUpload(file: File | null) {
    if (!file) {
      setErrorMessage("Select a resume file before uploading.");
      return;
    }
    setErrorMessage(null);
    setStatusMessage("Uploading resume...");
    try {
      const resume = await runWithRefresh((token) => uploadResume(token, file));
      setResumes((prev) => [resume, ...prev]);
      setSelectedResumeId(resume.id);
      setStatusMessage("Resume uploaded successfully.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Resume upload failed");
    }
  }

  async function handleCreateJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setStatusMessage("Saving job description...");
    try {
      const job = await runWithRefresh((token) =>
        createJob(token, {
          title: jobTitle,
          company: jobCompany || undefined,
          description: jobDescription,
        }),
      );
      setJobs((prev) => [job, ...prev]);
      setSelectedJobId(job.id);
      setJobTitle("");
      setJobCompany("");
      setJobDescription("");
      setStatusMessage("Job description saved.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to save job description");
    }
  }

  async function handleRunAnalysis() {
    if (!selectedResumeId || !selectedJobId) {
      setErrorMessage("Select both a resume and a job description before analysis.");
      return;
    }

    setErrorMessage(null);
    setStatusMessage("Running analysis...");

    try {
      const analysis = await runWithRefresh((token) =>
        createAnalysis(token, selectedResumeId, selectedJobId),
      );
      setLatestAnalysis(analysis);
      setHistory((prev) => [analysis, ...prev]);
      setStatusMessage("Analysis completed.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Analysis failed");
    }
  }

  function logout() {
    tokenStorage.clear();
    setTokens(null);
    setUser(null);
    setResumes([]);
    setJobs([]);
    setHistory([]);
    setLatestAnalysis(null);
    setStatusMessage(null);
    setErrorMessage(null);
  }

  if (!tokens) {
    return (
      <main className="auth-layout">
        <AuthPanel
          onAuthenticated={(nextTokens) => {
            tokenStorage.set(nextTokens);
            setTokens(nextTokens);
          }}
        />
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h2>AI Resume Analyzer</h2>
          <p className="muted">{user ? `Signed in as ${user.email}` : "Loading profile..."}</p>
        </div>
        <button type="button" onClick={logout}>
          Logout
        </button>
      </header>

      {loading && <p className="muted">Loading workspace data...</p>}
      {statusMessage && <p className="status-ok">{statusMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <section className="dashboard-grid">
        <section className="panel">
          <h3>1) Upload Resume</h3>
          <p className="muted">Supported formats: PDF, DOCX</p>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(event) => {
              const selectedFile = event.target.files?.[0] ?? null;
              void handleResumeUpload(selectedFile);
            }}
          />
        </section>

        <section className="panel">
          <h3>2) Add Job Description</h3>
          <form className="form-grid" onSubmit={handleCreateJob}>
            <label>
              Role title
              <input
                value={jobTitle}
                onChange={(event) => setJobTitle(event.target.value)}
                required
                minLength={2}
              />
            </label>
            <label>
              Company (optional)
              <input
                value={jobCompany}
                onChange={(event) => setJobCompany(event.target.value)}
              />
            </label>
            <label>
              Job description
              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                required
                minLength={20}
              />
            </label>
            <button type="submit">Save Job Description</button>
          </form>
        </section>

        <section className="panel">
          <h3>3) Analyze Match</h3>
          <div className="form-grid">
            <label>
              Resume
              <select
                value={selectedResumeId}
                onChange={(event) => setSelectedResumeId(event.target.value)}
                disabled={resumes.length === 0}
              >
                {resumes.length === 0 && <option value="">No resumes uploaded</option>}
                {resumes.map((resume) => (
                  <option key={resume.id} value={resume.id}>
                    {resume.filename}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Job description
              <select
                value={selectedJobId}
                onChange={(event) => setSelectedJobId(event.target.value)}
                disabled={jobs.length === 0}
              >
                {jobs.length === 0 && <option value="">No job descriptions yet</option>}
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} {job.company ? `- ${job.company}` : ""}
                  </option>
                ))}
              </select>
            </label>

            <button type="button" onClick={handleRunAnalysis} disabled={!hasDataToAnalyze}>
              Run Analysis
            </button>
          </div>
        </section>

        {latestAnalysis && (
          <section className="panel">
            <h3>Latest Analysis Result</h3>
            <p className="result-score">{latestAnalysis.suitability_score}</p>
            <p>{latestAnalysis.summary}</p>
            <p className="muted">Provider: {latestAnalysis.provider_used}</p>

            <div className="columns">
              <div>
                <h4>Strengths</h4>
                <div className="chip-list">
                  {latestAnalysis.strengths.map((item) => (
                    <span key={item} className="chip matched">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4>Gaps</h4>
                <div className="chip-list">
                  {latestAnalysis.gaps.map((item) => (
                    <span key={item} className="chip missing">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <h4>Keyword Breakdown</h4>
            <div className="chip-list">
              {latestAnalysis.keyword_breakdown.map((item) => (
                <span
                  key={item.keyword}
                  className={`chip ${item.matched ? "matched" : "missing"}`}
                >
                  {item.keyword}: {item.matched ? "matched" : "missing"}
                </span>
              ))}
            </div>
          </section>
        )}

        <HistoryPanel analyses={history} />
      </section>
    </main>
  );
}
