-- Active: 1773290431047@@127.0.0.1@5432@demo4_auth
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password_hash VARCHAR(255) NOT NULL CHECK (password_hash LIKE 'pbkdf2_sha256$%'),
    is_member BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_member BOOLEAN NOT NULL DEFAULT FALSE;

CREATE UNIQUE INDEX IF NOT EXISTS uk_users_username ON users (username);

CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(64) NOT NULL,
    industry_primary VARCHAR(64) NOT NULL DEFAULT '',
    industry_secondary VARCHAR(64) NOT NULL DEFAULT '',
    budget VARCHAR(32) NOT NULL DEFAULT '',
    rent_term VARCHAR(32) NOT NULL DEFAULT '',
    rent_mode VARCHAR(32) NOT NULL DEFAULT '',
    manpower VARCHAR(32) NOT NULL DEFAULT '',
    time_input VARCHAR(32) NOT NULL DEFAULT '',
    profit_per_customer VARCHAR(32) NOT NULL DEFAULT '',
    target_audience VARCHAR(64) NOT NULL DEFAULT '',
    has_channel VARCHAR(16) NOT NULL DEFAULT '',
    differentiation VARCHAR(16) NOT NULL DEFAULT '',
    differentiation_type VARCHAR(64) NOT NULL DEFAULT '',
    payback_period VARCHAR(32) NOT NULL DEFAULT '',
    time_cost_points JSONB NOT NULL DEFAULT '[]'::jsonb,
    time_profit_points JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS time_cost_points JSONB NOT NULL DEFAULT '[]'::jsonb;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS time_profit_points JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports (user_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports (created_at);
