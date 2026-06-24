import { get, post } from "../../../shared/api/httpClient";
import type { ApiResponse, CalendarResponse, GeneratePlanResponse, StudyPlanExplanationResponse, TodayResponse } from "../types/planning";

export function generateStudyPlan(input: {
  goal_id: string;
  plan_title?: string | null;
  include_revision_sessions: boolean;
  preferred_session_minutes: number;
}) {
  return post<ApiResponse<GeneratePlanResponse>>("/plans/generate", input);
}

export function fetchStudyCalendar(planId: string) {
  return get<ApiResponse<CalendarResponse>>(`/plans/${planId}/calendar`);
}

export function fetchTodayTasks(planId: string) {
  return get<ApiResponse<TodayResponse>>(`/plans/${planId}/today`);
}

export function explainStudyPlan(planId: string) {
  return post<ApiResponse<StudyPlanExplanationResponse>>(`/plans/${planId}/explain`, {});
}
