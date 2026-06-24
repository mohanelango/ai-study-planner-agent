import { FormEvent, useState } from "react";

import { post } from "../shared/api/httpClient";

type ApiResponse<T> = { success: boolean; message: string; data: T };

type RegisterData = {
  user_id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
};

export function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const response = await post<ApiResponse<RegisterData>>("/auth/register", {
        email,
        password,
        full_name: fullName || null,
      });
      setMessage(`${response.message}: ${response.data.email}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Registration failed");
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Auth</p>
      <h1>Register</h1>
      <form onSubmit={onSubmit} className="stacked-form">
        <label>Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label>
        <label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} required /></label>
        <label>Full name<input value={fullName} onChange={(event) => setFullName(event.target.value)} /></label>
        <button type="submit">Create account</button>
      </form>
      {message ? <p className="status success">{message}</p> : null}
      {error ? <p className="status error">{error}</p> : null}
    </section>
  );
}

