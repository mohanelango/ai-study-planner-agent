import { FormEvent, useState } from "react";

import { explainStudyPlan, generateStudyPlan } from "../services/planningApi";
import type { GeneratePlanResponse, StudyPlanExplanationResponse } from "../types/planning";

export function StudyPlanPage() {
  const [goalId, setGoalId] = useState("");
  const [planTitle, setPlanTitle] = useState("");
  const [preferredMinutes, setPreferredMinutes] = useState("60");
  const [includeRevision, setIncludeRevision] = useState(true);
  const [result, setResult] = useState<GeneratePlanResponse | null>(null);
  const [explanation, setExplanation] = useState<StudyPlanExplanationResponse | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setResult(null);
    try {
      const response = await generateStudyPlan({
        goal_id: goalId,
        plan_title: planTitle || null,
        include_revision_sessions: includeRevision,
        preferred_session_minutes: Number(preferredMinutes),
      });
      setResult(response.data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not generate study plan");
    }
  }

  async function generateExplanation(planId: string) {
    setError(null);
    setIsExplaining(true);
    setExplanation(null);
    try {
      const response = await explainStudyPlan(planId);
      setExplanation(response.data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not generate AI explanation");
    } finally {
      setIsExplaining(false);
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Planning</p>
      <h1>Generate Study Plan</h1>
      <form onSubmit={onSubmit} className="stacked-form">
        <label>Goal ID<input value={goalId} onChange={(event) => setGoalId(event.target.value)} required /></label>
        <label>Plan title<input value={planTitle} onChange={(event) => setPlanTitle(event.target.value)} /></label>
        <label>Preferred session minutes<input value={preferredMinutes} onChange={(event) => setPreferredMinutes(event.target.value)} type="number" min="30" max="180" /></label>
        <label className="checkbox-label"><input checked={includeRevision} onChange={(event) => setIncludeRevision(event.target.checked)} type="checkbox" /> Include revision sessions</label>
        <button type="submit">Generate Study Plan</button>
      </form>
      {error ? <p className="status error">{error}</p> : null}
      {result ? (
        <div className="status-panel wide-panel">
          <strong>{result.summary}</strong>
          <span>Total sessions: {result.total_sessions}</span>
          <span>Total tasks: {result.total_tasks}</span>
          {result.warnings.length ? <p className="status error">{result.warnings.join(" ")}</p> : null}
          <a className="button-link" href={`/plans/${result.study_plan_id}/calendar`}>View calendar</a>
          <a className="button-link secondary" href={`/plans/${result.study_plan_id}/today`}>View today&apos;s tasks</a>
          <button type="button" onClick={() => generateExplanation(result.study_plan_id)} disabled={isExplaining}>
            {isExplaining ? "Generating explanation..." : "Generate AI Explanation"}
          </button>
        </div>
      ) : null}
      {explanation ? (
        <div className="status-panel wide-panel explanation-panel">
          <h2>{explanation.headline}</h2>
          <p>{explanation.summary}</p>
          <strong>Priority rationale</strong>
          <ul>{explanation.priority_rationale.map((item) => <li key={item}>{item}</li>)}</ul>
          <strong>Schedule rationale</strong>
          <ul>{explanation.schedule_rationale.map((item) => <li key={item}>{item}</li>)}</ul>
          <strong>Risk warnings</strong>
          <ul>{explanation.risk_warnings.map((item) => <li key={item}>{item}</li>)}</ul>
          <strong>Next best actions</strong>
          <ul>{explanation.next_best_actions.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      ) : null}
    </section>
  );
}
