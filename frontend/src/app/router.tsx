import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { GoalSetupPage } from "../pages/GoalSetupPage";
import { HealthPage } from "../pages/HealthPage";
import { LoginPage } from "../pages/LoginPage";
import { ProfileSetupPage } from "../pages/ProfileSetupPage";
import { RegisterPage } from "../pages/RegisterPage";
import { StudyCalendarPage } from "../features/planning/pages/StudyCalendarPage";
import { StudyPlanPage } from "../features/planning/pages/StudyPlanPage";
import { TodayTasksPage } from "../features/planning/pages/TodayTasksPage";

export function Router() {
  const path = window.location.pathname;

  let page = <DashboardPage />;
  if (path === "/health") page = <HealthPage />;
  if (path === "/register") page = <RegisterPage />;
  if (path === "/login") page = <LoginPage />;
  if (path === "/profile") page = <ProfileSetupPage />;
  if (path === "/goals/setup") page = <GoalSetupPage />;
  if (path === "/plans") page = <StudyPlanPage />;
  if (/^\/plans\/[^/]+\/calendar$/.test(path)) page = <StudyCalendarPage />;
  if (/^\/plans\/[^/]+\/today$/.test(path)) page = <TodayTasksPage />;

  return <AppLayout>{page}</AppLayout>;
}
