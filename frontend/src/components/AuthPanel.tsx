import { FormEvent, useState } from "react";

import { ApiError } from "../api/client";
import { loginUser, registerUser } from "../api/auth";
import type { TokenPair } from "../types/models";

type Props = {
  onAuthenticated: (tokens: TokenPair) => void;
};

type Mode = "login" | "register";

export default function AuthPanel({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === "register") {
        await registerUser({ email, password });
      }
      const tokens = await loginUser({ email, password });
      onAuthenticated(tokens);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to authenticate. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="auth-card">
      <h1>AI Resume Analyzer</h1>
      <p className="muted">
        Upload your resume, compare it against job requirements, and get a structured suitability score.
      </p>

      <div className="mode-toggle">
        <button
          type="button"
          className={mode === "login" ? "active" : ""}
          onClick={() => setMode("login")}
        >
          Login
        </button>
        <button
          type="button"
          className={mode === "register" ? "active" : ""}
          onClick={() => setMode("register")}
        >
          Register
        </button>
      </div>

      <form onSubmit={onSubmit} className="auth-form">
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={12}
          />
        </label>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
        </button>
      </form>
    </section>
  );
}
