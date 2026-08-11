-- DDL Schema Setup for Meeting Mind AI
-- Paste this script directly inside the Supabase SQL Editor and click 'Run'.

-- 1. Create meetings master table
CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    raw_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create action_items table
CREATE TABLE IF NOT EXISTS action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    task_title TEXT NOT NULL,
    assigned VARCHAR(255) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    effort VARCHAR(50) NOT NULL,
    timeline VARCHAR(255) NOT NULL,
    acceptance_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create decisions log table
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create project_risks table
CREATE TABLE IF NOT EXISTS project_risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    blocker TEXT NOT NULL,
    impact TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create performance indexes for faster relational queries
CREATE INDEX IF NOT EXISTS idx_action_items_meeting_id ON action_items(meeting_id);
CREATE INDEX IF NOT EXISTS idx_decisions_meeting_id ON decisions(meeting_id);
CREATE INDEX IF NOT EXISTS idx_project_risks_meeting_id ON project_risks(meeting_id);
