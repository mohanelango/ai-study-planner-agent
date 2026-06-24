import { FormEvent, useState } from "react";

import { post, setAccessToken } from "../shared/api/httpClient";

type ApiResponse<T> = { success: boolean; message: string; data: T };

type LoginData = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: { id: string; email: string; full_name: string | null };
};

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const response = await post<ApiResponse<LoginData>>("/auth/login", { email, password });
      setAccessToken(response.data.access_token);
      setMessage(`Logged in as ${response.data.user.email}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Login failed");
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Auth</p>
      <h1>Login</h1>
      <form onSubmit={onSubmit} className="stacked-form">
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label>
        <label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required /></label>
        <button type="submit">Login</button>
      </form>
      {message ? <p className="status success">{message}</p> : null}
      {error ? <p className="status error">{error}</p> : null}
    </section>
  );
}

