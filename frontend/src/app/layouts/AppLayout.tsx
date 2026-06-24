import type { ReactNode } from "react";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <main className="app-shell">
      <nav className="top-nav">
        <a href="/">Dashboard</a>
        <a href="/health">Health</a>
        <a href="/register">Register</a>
        <a href="/login">Login</a>
        <a href="/profile">Profile</a>
        <a href="/goals/setup">Goal Setup</a>
        <a href="/plans">Plans</a>
      </nav>
      {children}
    </main>
  );
}
