
-- Insert fake users with hashed passwords
INSERT INTO users (username, email, password, is_superadmin) VALUES 
('user1', 'user1@example.com', '$2b$12$4hflMyE0VNfvg7ZFKyPXnOCrgv1K7TnC5G4yngqR2W/GSCFhHW1ru', TRUE), 
('user2', 'user2@example.com', '$2b$12$EIeF49Yz50pYFaCAa9qEmeF1FckNyodrQbwf7quRwr5n1MNBBh7a2', FALSE), 
('user3', 'user3@example.com', '$2b$12$3KmYdMPy7vbD5wjXEy2op.z1nJFvOQl9g8AnmuAe1namWVgM1Q8si', FALSE), 
('user4', 'user4@example.com', '$2b$12$DfUw/7CIiDE.zTG9fO7.9uMmFCOtZtSQgjHeipLCn0HDmjpxry6m2', FALSE), 
('user5', 'user5@example.com', '$2b$12$kGyxAeaJxnDNvr3022rlGOutfOXE/dDpm.RS.y5RryEjI9HDmtzfS', FALSE), 
('user6', 'user6@example.com', '$2b$12$N2JiqpfSei8zxmUyBN/Dau3.I7b2TD3WgLsDI2gdxB7ACrGmDP.Nq', FALSE), 
('user7', 'user7@example.com', '$2b$12$8u8IaHmE18ftpYr7tPEe4eHHPQihXSdHQY/px17TDD7fa8y9dzHiS', FALSE), 
('user8', 'user8@example.com', '$2b$12$bYMBokWrcEQXMTt6EqHPTu4pFQGrPv7eIEkU5WZaRPDl1LdwJXxBq', FALSE), 
('user9', 'user9@example.com', '$2b$12$tmjCqMYu0geml8IQwDWAgetahC/pPsoQQmmXxyQn57Z6fzbxyqoyy', FALSE), 
('user10', 'user10@example.com', '$2b$12$BDhv.H1rCLrO1uM.fpIMNO2T30YGloEjH1FEOdOvNP6el9xASmfaq', FALSE);

-- Insert fake events
INSERT INTO events (name, description, start_time, end_time)
VALUES
('Launch Event', 'Launch event for the marketing campaign', '2024-01-01 09:00:00', '2024-01-01 12:00:00'),
('Team Competition', 'Team competition starts', '2024-02-01 10:00:00', '2024-02-01 18:00:00'),
('Final Awards', 'Awards ceremony for winning teams', '2024-03-01 14:00:00', '2024-03-01 16:00:00');


-- Insert fake teams
INSERT INTO teams (name, description, event_id)
VALUES
('Team Alpha', 'The Alpha team description', 1),
('Team Beta', 'The Beta team description', 1),
('Team Gamma', 'The Gamma team description', 2),
('Team Delta', 'The Delta team description', 2),
('Team Epsilon', 'The Epsilon team description', 3);


-- Insert fake user-team relationships
INSERT INTO user_teams (user_id, team_id)
VALUES
(1, 1),
(1, 2),
(2, 1),
(3, 3),
(4, 4),
(5, 5),
(6, 1),
(7, 2),
(8, 3),
(9, 4),
(10, 5);

-- Insert fake check-ins with photo URLs
INSERT INTO checkins (team_id, user_id, content, photo_url)
VALUES
(1, 1, 'Check-in 1 by user1 in team1', 'https://example.com/photos/checkin1.jpg'),
(1, 2, 'Check-in 2 by user2 in team1', 'https://example.com/photos/checkin2.jpg'),
(2, 1, 'Check-in 3 by user1 in team2', 'https://example.com/photos/checkin3.jpg'),
(2, 3, 'Check-in 4 by user3 in team2', 'https://example.com/photos/checkin4.jpg'),
(3, 4, 'Check-in 5 by user4 in team3', 'https://example.com/photos/checkin5.jpg'),
(4, 5, 'Check-in 6 by user5 in team4', 'https://example.com/photos/checkin6.jpg'),
(5, 6, 'Check-in 7 by user6 in team5', 'https://example.com/photos/checkin7.jpg'),
(5, 7, 'Check-in 8 by user7 in team5', 'https://example.com/photos/checkin8.jpg'),
(4, 8, 'Check-in 9 by user8 in team4', 'https://example.com/photos/checkin9.jpg'),
(3, 9, 'Check-in 10 by user9 in team3', 'https://example.com/photos/checkin10.jpg');

-- Insert fake scores
INSERT INTO scores (team_id, score)
VALUES
(1, 50.0),
(2, 40.5),
(3, 70.3),
(4, 60.2),
(5, 45.8);