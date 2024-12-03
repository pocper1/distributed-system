-- 1. Create 'users' table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create 'teams' table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create 'user_teams' table
CREATE TABLE user_teams (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    team_id INT NOT NULL,
    weight FLOAT DEFAULT 1.0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
);

-- 4. Create 'checkins' table
CREATE TABLE checkins (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 5. Create 'scores' table
CREATE TABLE scores (
    team_id INT PRIMARY KEY,
    score FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
);


-- Insert fake users
INSERT INTO users (username, email, password)
VALUES
('user1', 'user1@example.com', 'password1'),
('user2', 'user2@example.com', 'password2'),
('user3', 'user3@example.com', 'password3'),
('user4', 'user4@example.com', 'password4'),
('user5', 'user5@example.com', 'password5'),
('user6', 'user6@example.com', 'password6'),
('user7', 'user7@example.com', 'password7'),
('user8', 'user8@example.com', 'password8'),
('user9', 'user9@example.com', 'password9'),
('user10', 'user10@example.com', 'password10');

-- Insert fake teams
INSERT INTO teams (name, description)
VALUES
('Team Alpha', 'The Alpha team description'),
('Team Beta', 'The Beta team description'),
('Team Gamma', 'The Gamma team description'),
('Team Delta', 'The Delta team description'),
('Team Epsilon', 'The Epsilon team description');

-- Insert fake user-team relationships
INSERT INTO user_teams (user_id, team_id, weight)
VALUES
(1, 1, 1.0),
(1, 2, 0.5),
(2, 1, 1.0),
(3, 3, 1.0),
(4, 4, 1.0),
(5, 5, 1.0),
(6, 1, 1.0),
(7, 2, 0.8),
(8, 3, 0.5),
(9, 4, 1.0),
(10, 5, 0.7);

-- Insert fake check-ins
INSERT INTO checkins (team_id, user_id, content)
VALUES
(1, 1, 'Check-in 1 by user1 in team1'),
(1, 2, 'Check-in 2 by user2 in team1'),
(2, 1, 'Check-in 3 by user1 in team2'),
(2, 3, 'Check-in 4 by user3 in team2'),
(3, 4, 'Check-in 5 by user4 in team3'),
(4, 5, 'Check-in 6 by user5 in team4'),
(5, 6, 'Check-in 7 by user6 in team5'),
(5, 7, 'Check-in 8 by user7 in team5'),
(4, 8, 'Check-in 9 by user8 in team4'),
(3, 9, 'Check-in 10 by user9 in team3');

-- Insert fake scores
INSERT INTO scores (team_id, score)
VALUES
(1, 50.0),
(2, 40.5),
(3, 70.3),
(4, 60.2),
(5, 45.8);

