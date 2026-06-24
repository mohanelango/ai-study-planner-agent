CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS study_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_name TEXT NOT NULL,
    exam_date DATE NOT NULL,
    hours_per_week INTEGER NOT NULL CHECK (hours_per_week > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    subject TEXT NOT NULL,
    focus TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0)
);
