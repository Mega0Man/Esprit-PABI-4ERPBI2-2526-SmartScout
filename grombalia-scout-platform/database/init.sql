-- PostgreSQL Schema for Grombalia Scout Group
-- with Row-Level Security (RLS)

CREATE DATABASE grombalia_scout;
\c grombalia_scout;

-- Enable RLS
ALTER DATABASE grombalia_scout SET row_security = on;

-- Create user table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('group_leader', 'treasurer', 'unit_leader')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policy: users can only see their own data
CREATE POLICY users_select_policy ON users
    FOR SELECT
    USING (current_setting('app.current_user')::INTEGER = id);

-- Insert sample users
-- Passwords are 'password' hashed with bcrypt
INSERT INTO users (username, password_hash, role) VALUES
('group_leader', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyWJj5l5G5K', 'group_leader'),
('treasurer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyWJj5l5G5K', 'treasurer'),
('unit_leader', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyWJj5l5G5K', 'unit_leader');

-- Create ML inference logs table
CREATE TABLE ml_inference_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    inference_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on ml_inference_logs table
ALTER TABLE ml_inference_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy: users can only see their own logs
CREATE POLICY ml_logs_select_policy ON ml_inference_logs
    FOR SELECT
    USING (current_setting('app.current_user')::INTEGER = user_id);

-- Create RLS policy: users can only insert their own logs
CREATE POLICY ml_logs_insert_policy ON ml_inference_logs
    FOR INSERT
    WITH CHECK (current_setting('app.current_user')::INTEGER = user_id);
