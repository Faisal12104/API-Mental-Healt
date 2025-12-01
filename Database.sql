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

##################################################################################################################################################################################################################################################################################

USE mental_health_api;

-- Table mood_entries
CREATE TABLE IF NOT EXISTS mood_entries (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    mood ENUM('veryHappy', 'happy', 'neutral', 'sad', 'verySad', 'anxious', 'stressed', 'calm', 'excited', 'angry') NOT NULL,
    energy_level INT CHECK (energy_level BETWEEN 1 AND 10),
    sleep_hours DECIMAL(3,1) CHECK (sleep_hours BETWEEN 3 AND 12),
    activities JSON,
    tags JSON,
    note TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

-- Insert sample data untuk testing
INSERT INTO mood_entries (id, user_id, mood, energy_level, sleep_hours, activities, tags, note) VALUES
(UUID(), 'test-user-123', 'happy', 8, 7.5, '["exercise", "reading"]', '["productive", "motivated"]', 'Had a great workout this morning!'),
(UUID(), 'test-user-123', 'neutral', 6, 6.0, '["work", "socializing"]', '["busy", "tired"]', 'Long day at work but good meeting with friends'),
(UUID(), 'test-user-123', 'stressed', 4, 5.5, '["work"]', '["stressed", "overwhelmed"]', 'Too many deadlines this week'),
(UUID(), 'test-user-123', 'calm', 7, 8.0, '["reading", "hobby"]', '["relaxed", "creative"]', 'Nice relaxing evening with book'),
(UUID(), 'test-user-123', 'happy', 9, 7.0, '["exercise", "socializing"]', '["energetic", "social"]', 'Weekend vibes! Great day with friends');

##################################################################################################################################################################################################################################################################################

USE mental_health_api;

-- Table psychologists
CREATE TABLE IF NOT EXISTS psychologists (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialization JSON,
    experience INT,
    rating DECIMAL(3,2) DEFAULT 0.0,
    price_per_hour DECIMAL(10,2),
    languages JSON,
    availability JSON,
    avatar TEXT,
    bio TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table consultations
CREATE TABLE IF NOT EXISTS consultations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    psychologist_id VARCHAR(36) NOT NULL,
    type ENUM('chat', 'video', 'phone') NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled', 'rejected') DEFAULT 'pending',
    preferred_date DATE,
    preferred_time TIME,
    duration INT DEFAULT 60,
    reason TEXT,
    urgency ENUM('low', 'medium', 'high') DEFAULT 'medium',
    price DECIMAL(10,2),
    notes TEXT,
    scheduled_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (psychologist_id) REFERENCES psychologists(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_psychologist_id (psychologist_id),
    INDEX idx_status (status)
);

-- Table messages
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(36) PRIMARY KEY,
    consultation_id VARCHAR(36) NOT NULL,
    sender_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    type ENUM('text', 'image', 'file') DEFAULT 'text',
    attachments JSON,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE,
    INDEX idx_consultation_id (consultation_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_created_at (created_at)
);

-- Insert sample psychologists
INSERT INTO psychologists (id, name, specialization, experience, rating, price_per_hour, languages, availability, bio) VALUES
(
    UUID(),
    'Dr. Sarah Johnson',
    '["anxiety", "depression", "relationships"]',
    8,
    4.8,
    150000,
    '["Indonesian", "English"]',
    '{"monday": ["09:00-17:00"], "tuesday": ["09:00-17:00"], "wednesday": ["09:00-17:00"], "thursday": ["09:00-17:00"], "friday": ["09:00-15:00"]}',
    'Spesialis dalam menangani anxiety dan depression dengan pendekatan CBT. Berpengalaman 8 tahun membantu klien mencapai keseimbangan mental.'
),
(
    UUID(),
    'Dr. Ahmad Rahman',
    '["stress", "work-life balance", "career"]',
    6,
    4.6,
    120000,
    '["Indonesian", "Arabic"]',
    '{"monday": ["10:00-18:00"], "tuesday": ["10:00-18:00"], "wednesday": ["10:00-18:00"], "saturday": ["09:00-13:00"]}',
    'Fokus pada manajemen stress dan keseimbangan kerja-hidup. Menggunakan teknik mindfulness dan solution-focused therapy.'
),
(
    UUID(),
    'Dr. Maya Sari',
    '["trauma", "PTSD", "family issues"]',
    10,
    4.9,
    180000,
    '["Indonesian", "English"]',
    '{"tuesday": ["08:00-16:00"], "wednesday": ["08:00-16:00"], "thursday": ["08:00-16:00"], "friday": ["08:00-16:00"]}',
    'Ahli dalam menangani trauma dan PTSD dengan pendekatan EMDR. Pengalaman 10 tahun di bidang mental health.'
),
(
    UUID(),
    'Dr. Budi Santoso',
    '["addiction", "behavioral", "motivation"]',
    7,
    4.5,
    130000,
    '["Indonesian"]',
    '{"monday": ["13:00-21:00"], "tuesday": ["13:00-21:00"], "wednesday": ["13:00-21:00"], "thursday": ["13:00-21:00"]}',
    'Spesialis behavioral therapy dan addiction recovery. Membantu klien membangun kebiasaan positif dan motivasi.'
),
(
    UUID(),
    'Dr. Lisa Wijaya',
    '["teen issues", "education", "self-esteem"]',
    5,
    4.7,
    110000,
    '["Indonesian", "English", "Mandarin"]',
    '{"wednesday": ["09:00-17:00"], "thursday": ["09:00-17:00"], "friday": ["09:00-17:00"], "saturday": ["09:00-12:00"]}',
    'Berspesialisasi dalam masalah remaja dan pendidikan. Pendekatan yang friendly dan supportive untuk young adults.'
);

-- Insert sample consultation
INSERT INTO consultations (id, user_id, psychologist_id, type, status, preferred_date, preferred_time, duration, reason, urgency, price) 
SELECT 
    UUID(),
    'test-user-123',
    id,
    'video',
    'completed',
    CURDATE() - INTERVAL 7 DAY,
    '14:00:00',
    60,
    'Mengalami anxiety berlebihan dalam pekerjaan dan sulit tidur',
    'medium',
    price_per_hour
FROM psychologists 
LIMIT 1;

##################################################################################################################################################################################################################################################################################

USE mental_health_api;

-- Table forum_rooms
CREATE TABLE IF NOT EXISTS forum_rooms (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category ENUM('cinta', 'pekerjaan', 'keluarga', 'kesehatan', 'pendidikan', 'hobi', 'lainnya') NOT NULL,
    icon VARCHAR(10),
    member_count INT DEFAULT 0,
    post_count INT DEFAULT 0,
    last_activity TIMESTAMP NULL,
    is_private BOOLEAN DEFAULT FALSE,
    rules JSON,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_last_activity (last_activity)
);

-- Table forum_room_members
CREATE TABLE IF NOT EXISTS forum_room_members (
    id VARCHAR(36) PRIMARY KEY,
    room_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    role ENUM('member', 'moderator', 'admin') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES forum_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member (room_id, user_id),
    INDEX idx_room_id (room_id),
    INDEX idx_user_id (user_id)
);

-- Table forum_posts
CREATE TABLE IF NOT EXISTS forum_posts (
    id VARCHAR(36) PRIMARY KEY,
    room_id VARCHAR(36) NOT NULL,
    author_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    mood VARCHAR(10),
    tags JSON,
    attachments JSON,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES forum_rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_room_id (room_id),
    INDEX idx_author_id (author_id),
    INDEX idx_created_at (created_at)
);

-- Table forum_post_likes
CREATE TABLE IF NOT EXISTS forum_post_likes (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_like (post_id, user_id),
    INDEX idx_post_id (post_id)
);

-- Table forum_comments
CREATE TABLE IF NOT EXISTS forum_comments (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) NOT NULL,
    author_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    like_count INT DEFAULT 0,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_post_id (post_id),
    INDEX idx_author_id (author_id)
);

-- Table forum_comment_likes
CREATE TABLE IF NOT EXISTS forum_comment_likes (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES forum_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_comment_like (comment_id, user_id)
);

-- Table forum_reports
CREATE TABLE IF NOT EXISTS forum_reports (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36),
    comment_id VARCHAR(36),
    reporter_id VARCHAR(36) NOT NULL,
    reason ENUM('spam', 'inappropriate', 'harassment', 'other') NOT NULL,
    description TEXT,
    status ENUM('pending', 'reviewed', 'resolved') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (comment_id) REFERENCES forum_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert sample forum rooms
INSERT INTO forum_rooms (id, name, description, category, icon, member_count, post_count, rules, created_by) VALUES
(
    UUID(),
    'Curhat Cinta dan Relationship',
    'Ruang untuk berbagi cerita tentang hubungan asmara, percintaan, dan masalah relationship',
    'cinta',
    '💕',
    1250,
    89,
    '["Hormati privasi orang lain", "Dilarang menyebarkan informasi pribadi", "Jangan menghakimi", "Bebas berbagi tanpa judgement"]',
    'test-user-123'
),
(
    UUID(),
    'Diskusi Pekerjaan dan Karir',
    'Berbagi pengalaman kerja, masalah karir, dan mencari solusi bersama',
    'pekerjaan',
    '💼',
    890,
    45,
    '["Jaga profesionalisme", "Dilarang promosi bisnis", "Hargai perbedaan pendapat", "Berbagi pengalaman yang membangun"]',
    'test-user-123'
),
(
    UUID(),
    'Keluarga dan Parenting',
    'Ruang diskusi tentang keluarga, parenting, dan hubungan keluarga',
    'keluarga',
    '👨‍👩‍👧‍👦',
    670,
    32,
    '["Hormati perbedaan pola asuh", "Dilarang memberikan saran medis", "Fokus pada support dan berbagi"]',
    'test-user-123'
),
(
    UUID(),
    'Kesehatan Mental',
    'Diskusi tentang kesehatan mental, self-care, dan tips menjaga mental health',
    'kesehatan',
    '🧠',
    2100,
    156,
    '["Bukan pengganti konsultasi profesional", "Dilarang diagnosis", "Saling mendukung dan memotivasi"]',
    'test-user-123'
),
(
    UUID(),
    'Hobi dan Minat',
    'Berbagi hobi, kegiatan positif, dan minat untuk kesehatan mental',
    'hobi',
    '🎨',
    430,
    23,
    '["Berbagi kegiatan positif", "Saling menginspirasi", "Dukung kreativitas masing-masing"]',
    'test-user-123'
);

-- Insert sample posts
INSERT INTO forum_posts (id, room_id, author_id, content, is_anonymous, mood, tags, like_count, comment_count) 
SELECT 
    UUID(),
    id,
    'test-user-123',
    'Halo semua! Saya sedang mengalami masalah dalam relationship. Partner saya sering tidak komunikasi dan saya merasa diabaikan. Ada yang pernah mengalami hal serupa?',
    FALSE,
    '😢',
    '["relationship", "communication", "support"]',
    15,
    8
FROM forum_rooms 
WHERE category = 'cinta' 
LIMIT 1;

INSERT INTO forum_posts (id, room_id, author_id, content, is_anonymous, mood, tags, like_count, comment_count) 
SELECT 
    UUID(),
    id,
    'test-user-123',
    'Baru saja dapat tekanan kerja yang sangat berat. Deadline menumpuk dan atasan tidak memahami kondisi. Bagaimana cara kalian mengatasi stress kerja?',
    TRUE,
    '😰',
    '["work", "stress", "burnout"]',
    23,
    12
FROM forum_rooms 
WHERE category = 'pekerjaan' 
LIMIT 1;

-- Update last_activity for rooms
UPDATE forum_rooms 
SET last_activity = CURRENT_TIMESTAMP 
WHERE id IN (SELECT room_id FROM forum_posts);