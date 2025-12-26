-- A.B.E.L Database Initialization Script
-- This script runs when PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    google_access_token TEXT,
    google_refresh_token TEXT,
    twitter_access_token TEXT,
    instagram_session TEXT,
    preferred_voice_id VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Europe/Paris',
    language VARCHAR(10) DEFAULT 'fr',
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) DEFAULT 'New Conversation',
    summary TEXT,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    audio_url VARCHAR(500),
    audio_duration FLOAT,
    tokens INTEGER DEFAULT 0,
    memory_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create memories table (metadata for Qdrant vectors)
CREATE TABLE IF NOT EXISTS memories (
    id SERIAL PRIMARY KEY,
    vector_id VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    memory_type VARCHAR(50) DEFAULT 'conversation',
    source VARCHAR(255),
    conversation_id INTEGER,
    importance FLOAT DEFAULT 0.5,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social_posts table
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'draft',
    content TEXT NOT NULL,
    media_urls JSONB,
    is_reply BOOLEAN DEFAULT FALSE,
    reply_to_id VARCHAR(100),
    conversation_context TEXT,
    tone VARCHAR(30),
    sentiment_score FLOAT,
    published_id VARCHAR(100),
    published_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social_directives table
CREATE TABLE IF NOT EXISTS social_directives (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    original_message TEXT NOT NULL,
    sender_username VARCHAR(255) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    tone_analysis VARCHAR(30) NOT NULL,
    context_summary TEXT NOT NULL,
    suggested_responses JSONB,
    user_directive TEXT,
    generated_response TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP
);

-- Create api_skills table
CREATE TABLE IF NOT EXISTS api_skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    documentation_url VARCHAR(500),
    auth_type VARCHAR(50),
    requires_auth BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_free BOOLEAN DEFAULT TRUE,
    cors_enabled BOOLEAN DEFAULT FALSE,
    last_ping TIMESTAMP,
    ping_success BOOLEAN DEFAULT FALSE,
    response_time_ms FLOAT,
    endpoints JSONB,
    example_calls JSONB,
    tags JSONB,
    call_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 1.0,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_memories_vector_id ON memories(vector_id);
CREATE INDEX IF NOT EXISTS idx_memories_memory_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_api_skills_category ON api_skills(category);
CREATE INDEX IF NOT EXISTS idx_api_skills_is_active ON api_skills(is_active);

-- Insert default admin user (password: changeme)
INSERT INTO users (email, username, hashed_password, is_admin)
VALUES ('admin@abel.local', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G2i5xKaVp1s5Aq', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'A.B.E.L Database initialized successfully!';
END $$;
