import { FormEvent, useState } from "react";

import { post, put } from "../shared/api/httpClient";

type ApiResponse<T> = { success: boolean; message: string; data: T };

type ProfileData = {
  id: string;
  education_level: string | null;
  timezone: string;
  preferred_study_duration_minutes: number | null;
  learning_style: string | null;
  daily_goal_minutes: number | null;
};

export function ProfileSetupPage() {
  const [educationLevel, setEducationLevel] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [duration, setDuration] = useState("45");
  const [learningStyle, setLearningStyle] = useState("");
  const [dailyGoal, setDailyGoal] = useState("90");
  const [dayOfWeek, setDayOfWeek] = useState("1");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const profilePayload = {
    education_level: educationLevel || null,
    timezone,
    preferred_study_duration_minutes: duration ? Number(duration) : null,
    learning_style: learningStyle || null,
    daily_goal_minutes: dailyGoal ? Number(dailyGoal) : null,
  };

  async function createProfile(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const response = await post<ApiResponse<ProfileData>>("/profiles", profilePayload);
      setMessage(`Profile saved: ${response.data.timezone}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Profile save failed");
    }
  }

  async function updateProfile() {
    setError(null);
    try {
      const response = await put<ApiResponse<ProfileData>>("/profiles/me", profilePayload);
      setMessage(`Profile updated: ${response.data.timezone}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Profile update failed");
    }
  }

  async function addAvailability() {
    setError(null);
    try {
      await post<ApiResponse<unknown>>("/availability", {
        day_of_week: Number(dayOfWeek),
        start_time: startTime,
        end_time: endTime,
      });
      setMessage("Availability added");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Availability save failed");
    }
  }

  return (
    <section className="hero-card form-card">
      <p className="eyebrow">Profile</p>
      <h1>Profile Setup</h1>
      <form onSubmit={createProfile} className="stacked-form">
        <label>Education level<input value={educationLevel} onChange={(event) => setEducationLevel(event.target.value)} /></label>
        <label>Timezone<input value={timezone} onChange={(event) => setTimezone(event.target.value)} required /></label>
        <label>Study duration minutes<input value={duration} onChange={(event) => setDuration(event.target.value)} type="number" min="1" /></label>
        <label>Learning style<input value={learningStyle} onChange={(event) => setLearningStyle(event.target.value)} /></label>
        <label>Daily goal minutes<input value={dailyGoal} onChange={(event) => setDailyGoal(event.target.value)} type="number" min="1" /></label>
        <div className="button-row"><button type="submit">Create profile</button><button type="button" onClick={updateProfile}>Update profile</button></div>
      </form>
      <h2>Add availability</h2>
      <div className="stacked-form">
        <label>Day of week<input value={dayOfWeek} onChange={(event) => setDayOfWeek(event.target.value)} type="number" min="0" max="6" /></label>
        <label>Start time<input value={startTime} onChange={(event) => setStartTime(event.target.value)} type="time" /></label>
        <label>End time<input value={endTime} onChange={(event) => setEndTime(event.target.value)} type="time" /></label>
        <button type="button" onClick={addAvailability}>Add availability</button>
      </div>
      {message ? <p className="status success">{message}</p> : null}
      {error ? <p className="status error">{error}</p> : null}
    </section>
  );
}

