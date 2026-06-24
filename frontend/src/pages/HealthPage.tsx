import { useEffect, useState } from "react";

import { get } from "../shared/api/httpClient";

type HealthResponse = {
  success: boolean;
  message: string;
  data: {
    service: string;
    status: string;
  };
};

export function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    get<HealthResponse>("/health")
      .then(setHealth)
      .catch((caught: unknown) => {
        setError(caught instanceof Error ? caught.message : "Unable to reach backend");
      });
  }, []);

  return (
    <section className="hero-card">
      <p className="eyebrow">Backend</p>
      <h1>Health Check</h1>
      {error ? <p className="status error">{error}</p> : null}
      {!health && !error ? <p className="status">Checking backend status...</p> : null}
      {health ? (
        <div className="status-panel">
          <strong>{health.data.service}</strong>
          <span>{health.message}</span>
          <code>{health.data.status}</code>
        </div>
      ) : null}
    </section>
  );
}

