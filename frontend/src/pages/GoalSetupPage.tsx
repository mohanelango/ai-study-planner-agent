import { FormEvent, useState } from "react";

import { post } from "../shared/api/httpClient";

type ApiResponse<T> = { success: boolean; message: string; data: T };

type GoalData = { id: string; title: string };
type SubjectData = { id: string; goal_id: string; name: string };
type TopicData = { id: string; subject_id: string; goal_id: string; name: string };

export function GoalSetupPage() {
  const [goalId, setGoalId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [title, setTitle] = useState("Prepare for exam");
  const [examDate, setExamDate] = useState("2026-12-31");
  const [targetScore, setTargetScore] = useState("");
  const [subjectName, setSubjectName] = useState("Mathematics");
  const [topicName, setTopicName] = useState("Algebra");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function createGoal(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const response = await post<ApiResponse<GoalData>>("/goals", {
        title,
        description: null,
        exam_date: examDate,
        target_score: targetScore || null,
      });
      setGoalId(response.data.id);
      setMessage(`Goal created: ${response.data.title}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Goal create failed");
    }
  }

  async function addSubject() {
    setError(null);
    try {
      const response = await post<ApiResponse<SubjectData>>(`/goals/${goalId}/subjects`, {
        name: subjectName,
        description: null,
        priority: 3,
      });
      setSubjectId(response.data.id);
      setMessage(`Subject added: ${response.data.name}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Subject create failed");
    }
  }

  async function addTopic() {
    setError(null);
    try {
      const response = await post<ApiResponse<TopicData>>(`/subjects/${subjectId}/topics`, {
        name: topicName,
        description: null,
        difficulty: 3,
        priority: 3,
        estimated_hours: 2,
        is_manually_marked_weak: false,
      });
      setMessage(`Topic added: ${response.data.name}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Topic create failed");
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Goals</p>
      <h1>Goal Setup</h1>
      <form onSubmit={createGoal} className="stacked-form">
        <label>Goal title<input value={title} onChange={(event) => setTitle(event.target.value)} required /></label>
        <label>Exam date<input value={examDate} onChange={(event) => setExamDate(event.target.value)} type="date" required /></label>
        <label>Target score<input value={targetScore} onChange={(event) => setTargetScore(event.target.value)} /></label>
        <button type="submit">Create goal</button>
      </form>
      <h2>Add subject</h2>
      <div className="stacked-form">
        <label>Goal ID<input value={goalId} onChange={(event) => setGoalId(event.target.value)} /></label>
        <label>Subject name<input value={subjectName} onChange={(event) => setSubjectName(event.target.value)} /></label>
        <button type="button" onClick={addSubject}>Add subject</button>
      </div>
      <h2>Add topic</h2>
      <div className="stacked-form">
        <label>Subject ID<input value={subjectId} onChange={(event) => setSubjectId(event.target.value)} /></label>
        <label>Topic name<input value={topicName} onChange={(event) => setTopicName(event.target.value)} /></label>
        <button type="button" onClick={addTopic}>Add topic</button>
      </div>
      {message ? <p className="status success">{message}</p> : null}
      {error ? <p className="status error">{error}</p> : null}
    </section>
  );
}

