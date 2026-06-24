import { useEffect, useState } from "react";

import { fetchTodayTasks } from "../services/planningApi";
import type { ApiResponse, TodayResponse } from "../types/planning";

function getPlanIdFromPath(): string {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[1] ?? "";
}

export function TodayTasksPage() {
  const [planId] = useState(getPlanIdFromPath());
  const [today, setToday] = useState<TodayResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!planId) return;
    fetchTodayTasks(planId)
      .then((response: ApiResponse<TodayResponse>) => setToday(response.data))
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Could not fetch today's tasks"));
  }, [planId]);

  return (
    <section className="hero-card">
      <p className="eyebrow">Today</p>
      <h1>Today's Tasks</h1>
      {error ? <p className="status error">{error}</p> : null}
      {!today && !error ? <p className="status">Loading today's tasks...</p> : null}
      {today ? (
        <div className="calendar-list">
          <p className="subtitle">{today.date}</p>
          {today.sessions.length === 0 ? <p className="status">No sessions scheduled for today.</p> : null}
          {today.sessions.map((session) => (
            <article className="feature-card" key={session.session_id}>
              <h2>{session.start_time ?? "Any time"} · {session.session_type}</h2>
              <ul>
                {session.tasks.map((task) => (
                  <li key={task.task_id}>{task.title} — {task.planned_duration_minutes} min</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
