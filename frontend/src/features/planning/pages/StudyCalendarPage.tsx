import { useEffect, useState } from "react";

import { fetchStudyCalendar } from "../services/planningApi";
import type { ApiResponse, CalendarResponse } from "../types/planning";

function getPlanIdFromPath(): string {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[1] ?? "";
}

export function StudyCalendarPage() {
  const [planId] = useState(getPlanIdFromPath());
  const [calendar, setCalendar] = useState<CalendarResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!planId) return;
    fetchStudyCalendar(planId)
      .then((response: ApiResponse<CalendarResponse>) => setCalendar(response.data))
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Could not fetch calendar"));
  }, [planId]);

  return (
    <section className="hero-card">
      <p className="eyebrow">Calendar</p>
      <h1>Study Calendar</h1>
      {error ? <p className="status error">{error}</p> : null}
      {!calendar && !error ? <p className="status">Loading calendar...</p> : null}
      {calendar ? (
        <div className="calendar-list">
          {calendar.sessions.map((session) => (
            <article className="feature-card" key={session.session_id}>
              <h2>{session.session_date} · {session.session_type}</h2>
              <p>{session.start_time ?? "Any time"} - {session.end_time ?? ""} · {session.planned_duration_minutes} min · {session.status}</p>
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
