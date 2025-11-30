USE mental_health_api;

-- Hapus tables jika ada
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS users;

-- Buat table users
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other'),
    avatar TEXT,
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Buat table refresh_tokens
CREATE TABLE refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Test insert
INSERT INTO users (id, name, email, password, phone, date_of_birth, gender, preferences) 
VALUES (
    'test-id-123', 
    'Test User', 
    'test@example.com', 
    'hashed_password',
    '08123456789',
    '1990-01-01',
    'male',
    '{"notifications": true}'
);

SELECT * FROM users;
SELECT * FROM refresh_tokens;