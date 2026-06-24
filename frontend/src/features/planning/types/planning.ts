export type ApiResponse<T> = { success: boolean; message: string; data: T };

export type GeneratePlanResponse = {
  study_plan_id: string;
  active_version_id: string;
  version_number: number;
  summary: string;
  warnings: string[];
  total_sessions: number;
  total_tasks: number;
};

export type StudyTask = {
  task_id: string;
  topic_id: string | null;
  subject_id: string | null;
  title: string;
  description: string | null;
  task_type: string;
  status: string;
  planned_duration_minutes: number;
  sort_order: number;
};

export type StudySession = {
  session_id: string;
  session_date: string;
  start_time: string | null;
  end_time: string | null;
  session_type: string;
  status: string;
  planned_duration_minutes: number;
  tasks: StudyTask[];
};

export type CalendarResponse = {
  plan_id: string;
  version_id: string;
  sessions: StudySession[];
};

export type TodayResponse = {
  date: string;
  sessions: StudySession[];
};

export type StudyPlanExplanationResponse = {
  agent_run_id: string;
  study_plan_id: string;
  version_id: string;
  headline: string;
  summary: string;
  priority_rationale: string[];
  schedule_rationale: string[];
  risk_warnings: string[];
  next_best_actions: string[];
  generated_at: string;
};
