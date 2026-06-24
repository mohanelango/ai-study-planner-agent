import { getAccessToken } from "../shared/api/httpClient";

const cards = [
  "Study Planning",
  "RAG Notes",
  "Quiz Generation",
  "Progress Tracking",
  "Adaptive Replanning",
  "AI Coach",
];

export function DashboardPage() {
  const isLoggedIn = Boolean(getAccessToken());

  return (
    <section className="hero-card">
      <p className="eyebrow">Resume-Optimized AI Portfolio Project</p>
      <h1>AI Study Planner Agent</h1>
      <p className="subtitle">Modular Monolith + Workers</p>
      <p className={isLoggedIn ? "status success" : "status"}>
        {isLoggedIn ? "Logged in with local access token." : "Not logged in. Register or login to try Weekend 3 setup."}
      </p>

      <div className="card-grid">
        {cards.map((card) => (
          <article className="feature-card" key={card}>
            <h2>{card}</h2>
            <p>Placeholder module for later MVP milestones.</p>
          </article>
        ))}
      </div>
    </section>
  );
}
