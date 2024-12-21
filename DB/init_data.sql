-- Drop tables if they already exist (in correct dependency order)
DROP TABLE IF EXISTS checkins CASCADE;
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS user_teams CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Create 'users' table with 'is_superadmin' column
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_superadmin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create 'events' table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create 'teams' table with foreign key relationship to 'events'
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    event_id INT NOT NULL,  -- Foreign key referencing events
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE  -- Establishes the relationship to events
);

-- 4. Create 'user_teams' table to represent many-to-many relationship between users and teams
CREATE TABLE user_teams (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
);

-- 5. Create 'checkins' table with 'photo_url' column
CREATE TABLE checkins (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    photo_url VARCHAR(255) NOT NULL, -- New photo URL column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 6. Create 'scores' table to track the score of each team
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,              -- 新增自增主鍵
    team_id INT UNIQUE NOT NULL,        -- 保證每個隊伍僅有一條記錄
    score FLOAT DEFAULT 0.0,            -- 分數
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 更新時間
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE -- 設置外鍵約束
);
