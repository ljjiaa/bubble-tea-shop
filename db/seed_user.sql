DELETE FROM app_users WHERE username = 'manager1';

INSERT INTO app_users (username, password_hash, role)
VALUES ('manager1', '$2b$12$qDxEcoJLPaakvuUBcg/ix.T0ibhmyaXqaYtu7ZVnzqy8/FoH/rTmm', 'manager');