from app.database import db
from mysql.connector import Error
import json

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    connection = db.get_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith('SELECT'):
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid or True
        
        return result
    except Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()

# User operations
def create_user(user_data: dict):
    query = """
    INSERT INTO users (id, name, email, password, phone, date_of_birth, gender, avatar, preferences)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Convert preferences to JSON string
    preferences_str = json.dumps(user_data.get('preferences', {}))
    
    params = (
        user_data['id'], 
        user_data['name'], 
        user_data['email'], 
        user_data['password'], 
        user_data.get('phone'), 
        user_data.get('date_of_birth'),
        user_data.get('gender'), 
        user_data.get('avatar'), 
        preferences_str
    )
    return execute_query(query, params)

def get_user_by_email(email: str):
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_query(query, (email,), fetch_one=True)
    
    # Parse JSON preferences back to dict
    if result and 'preferences' in result and result['preferences']:
        try:
            result['preferences'] = json.loads(result['preferences'])
        except:
            result['preferences'] = {}
    
    return result

def get_user_by_id(user_id: str):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,), fetch_one=True)
    
    # Parse JSON preferences back to dict
    if result and 'preferences' in result and result['preferences']:
        try:
            result['preferences'] = json.loads(result['preferences'])
        except:
            result['preferences'] = {}
    
    return result

def update_user(user_id: str, update_data: dict):
    if not update_data:
        return None
    
    # Handle preferences conversion
    if 'preferences' in update_data:
        update_data['preferences'] = json.dumps(update_data['preferences'])
        
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (user_id,)
    return execute_query(query, params)

# Refresh token operations
def create_refresh_token_db(token_data: dict):
    query = """
    INSERT INTO refresh_tokens (id, user_id, token, expires_at)
    VALUES (%s, %s, %s, %s)
    """
    params = (token_data['id'], token_data['user_id'], token_data['token'], token_data['expires_at'])
    return execute_query(query, params)

def get_refresh_token(token: str):
    query = "SELECT * FROM refresh_tokens WHERE token = %s"
    return execute_query(query, (token,), fetch_one=True)

def delete_refresh_token(token: str):
    query = "DELETE FROM refresh_tokens WHERE token = %s"
    return execute_query(query, (token,))

def delete_user_refresh_tokens(user_id: str):
    query = "DELETE FROM refresh_tokens WHERE user_id = %s"
    return execute_query(query, (user_id,))

# Mood entries operations
def create_mood_entry(mood_data: dict):
    query = """
    INSERT INTO mood_entries (id, user_id, mood, energy_level, sleep_hours, activities, tags, note, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    activities_str = json.dumps(mood_data.get('activities', []))
    tags_str = json.dumps(mood_data.get('tags', []))
    
    params = (
        mood_data['id'],
        mood_data['user_id'],
        mood_data['mood'],
        mood_data.get('energy_level'),
        mood_data.get('sleep_hours'),
        activities_str,
        tags_str,
        mood_data.get('note'),
        mood_data.get('timestamp')
    )
    return execute_query(query, params)

def get_mood_entries(user_id: str, start_date: str = None, end_date: str = None, page: int = 1, limit: int = 20):
    query = "SELECT * FROM mood_entries WHERE user_id = %s"
    params = [user_id]
    
    if start_date and end_date:
        query += " AND DATE(timestamp) BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND DATE(timestamp) >= %s"
        params.append(start_date)
    elif end_date:
        query += " AND DATE(timestamp) <= %s"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, (page - 1) * limit])
    
    return execute_query(query, tuple(params))

def get_mood_entry_by_id(entry_id: str):
    query = "SELECT * FROM mood_entries WHERE id = %s"
    return execute_query(query, (entry_id,), fetch_one=True)

def update_mood_entry(entry_id: str, update_data: dict):
    if not update_data:
        return None
    
    # Handle JSON fields
    if 'activities' in update_data:
        update_data['activities'] = json.dumps(update_data['activities'])
    if 'tags' in update_data:
        update_data['tags'] = json.dumps(update_data['tags'])
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE mood_entries SET {set_clause} WHERE id = %s"
    params = tuple(update_data.values()) + (entry_id,)
    return execute_query(query, params)

def delete_mood_entry(entry_id: str):
    query = "DELETE FROM mood_entries WHERE id = %s"
    return execute_query(query, (entry_id,))

def get_mood_statistics(user_id: str, start_date: str, end_date: str):
    query = """
    SELECT 
        COUNT(*) as total_entries,
        AVG(CASE 
            WHEN mood = 'veryHappy' THEN 10
            WHEN mood = 'happy' THEN 8
            WHEN mood = 'excited' THEN 9
            WHEN mood = 'calm' THEN 7
            WHEN mood = 'neutral' THEN 5
            WHEN mood = 'sad' THEN 3
            WHEN mood = 'verySad' THEN 1
            WHEN mood = 'anxious' THEN 2
            WHEN mood = 'stressed' THEN 2
            WHEN mood = 'angry' THEN 2
            ELSE 5
        END) as average_mood_score,
        AVG(energy_level) as average_energy,
        AVG(sleep_hours) as average_sleep,
        COUNT(CASE WHEN mood IN ('veryHappy', 'happy', 'excited', 'calm') THEN 1 END) as positive_days,
        COUNT(CASE WHEN mood IN ('sad', 'verySad', 'anxious', 'stressed', 'angry') THEN 1 END) as negative_days
    FROM mood_entries 
    WHERE user_id = %s AND DATE(timestamp) BETWEEN %s AND %s
    """
    return execute_query(query, (user_id, start_date, end_date), fetch_one=True)

def get_mood_distribution(user_id: str, start_date: str, end_date: str):
    query = """
    SELECT mood, COUNT(*) as count
    FROM mood_entries 
    WHERE user_id = %s AND DATE(timestamp) BETWEEN %s AND %s
    GROUP BY mood
    """
    return execute_query(query, (user_id, start_date, end_date))

# Psychologists operations
def create_psychologist(psychologist_data: dict):
    query = """
    INSERT INTO psychologists (id, name, specialization, experience, rating, price_per_hour, languages, availability, avatar, bio, is_available)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    specialization_str = json.dumps(psychologist_data.get('specialization', []))
    languages_str = json.dumps(psychologist_data.get('languages', []))
    availability_str = json.dumps(psychologist_data.get('availability', {}))
    
    params = (
        psychologist_data['id'],
        psychologist_data['name'],
        specialization_str,
        psychologist_data.get('experience', 0),
        psychologist_data.get('rating', 0.0),
        psychologist_data.get('price_per_hour'),
        languages_str,
        availability_str,
        psychologist_data.get('avatar'),
        psychologist_data.get('bio'),
        psychologist_data.get('is_available', True)
    )
    return execute_query(query, params)

def get_psychologists(specialization: str = None, available: bool = None, page: int = 1, limit: int = 20):
    query = "SELECT * FROM psychologists WHERE 1=1"
    params = []
    
    if specialization:
        query += " AND JSON_CONTAINS(specialization, %s)"
        params.append(f'"{specialization}"')
    
    if available is not None:
        query += " AND is_available = %s"
        params.append(available)
    
    query += " ORDER BY rating DESC LIMIT %s OFFSET %s"
    params.extend([limit, (page - 1) * limit])
    
    return execute_query(query, tuple(params))

def get_psychologist_by_id(psychologist_id: str):
    query = "SELECT * FROM psychologists WHERE id = %s"
    return execute_query(query, (psychologist_id,), fetch_one=True)

def update_psychologist(psychologist_id: str, update_data: dict):
    if not update_data:
        return None
    
    # Handle JSON fields
    if 'specialization' in update_data:
        update_data['specialization'] = json.dumps(update_data['specialization'])
    if 'languages' in update_data:
        update_data['languages'] = json.dumps(update_data['languages'])
    if 'availability' in update_data:
        update_data['availability'] = json.dumps(update_data['availability'])
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE psychologists SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (psychologist_id,)
    return execute_query(query, params)

# Consultations operations
def create_consultation(consultation_data: dict):
    query = """
    INSERT INTO consultations (id, user_id, psychologist_id, type, status, preferred_date, preferred_time, duration, reason, urgency, price)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    params = (
        consultation_data['id'],
        consultation_data['user_id'],
        consultation_data['psychologist_id'],
        consultation_data['type'],
        consultation_data.get('status', 'pending'),
        consultation_data.get('preferred_date'),
        consultation_data.get('preferred_time'),
        consultation_data.get('duration', 60),
        consultation_data.get('reason'),
        consultation_data.get('urgency', 'medium'),
        consultation_data.get('price')
    )
    return execute_query(query, params)

def get_consultations(user_id: str = None, psychologist_id: str = None, status: str = None, page: int = 1, limit: int = 20):
    query = "SELECT * FROM consultations WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    
    if psychologist_id:
        query += " AND psychologist_id = %s"
        params.append(psychologist_id)
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, (page - 1) * limit])
    
    return execute_query(query, tuple(params))

def get_consultation_by_id(consultation_id: str):
    query = "SELECT * FROM consultations WHERE id = %s"
    return execute_query(query, (consultation_id,), fetch_one=True)

def update_consultation(consultation_id: str, update_data: dict):
    if not update_data:
        return None
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE consultations SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (consultation_id,)
    return execute_query(query, params)

def get_consultation_statistics(user_id: str):
    query = """
    SELECT 
        COUNT(*) as total_sessions,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_sessions,
        COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as upcoming_sessions,
        COALESCE(SUM(duration), 0) as total_minutes,
        COALESCE(SUM(price), 0) as total_spent
    FROM consultations 
    WHERE user_id = %s
    """
    return execute_query(query, (user_id,), fetch_one=True)

# Messages operations
def create_message(message_data: dict):
    query = """
    INSERT INTO messages (id, consultation_id, sender_id, content, type, attachments, is_read)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    attachments_str = json.dumps(message_data.get('attachments', []))
    
    params = (
        message_data['id'],
        message_data['consultation_id'],
        message_data['sender_id'],
        message_data['content'],
        message_data.get('type', 'text'),
        attachments_str,
        message_data.get('is_read', False)
    )
    return execute_query(query, params)

def get_messages(consultation_id: str, page: int = 1, limit: int = 50):
    query = """
    SELECT * FROM messages 
    WHERE consultation_id = %s 
    ORDER BY created_at ASC 
    LIMIT %s OFFSET %s
    """
    return execute_query(query, (consultation_id, limit, (page - 1) * limit))

def mark_messages_as_read(consultation_id: str, user_id: str):
    query = """
    UPDATE messages 
    SET is_read = TRUE, read_at = CURRENT_TIMESTAMP 
    WHERE consultation_id = %s AND sender_id != %s AND is_read = FALSE
    """
    return execute_query(query, (consultation_id, user_id))

def get_unread_message_count(consultation_id: str, user_id: str):
    query = """
    SELECT COUNT(*) as unread_count 
    FROM messages 
    WHERE consultation_id = %s AND sender_id != %s AND is_read = FALSE
    """
    result = execute_query(query, (consultation_id, user_id), fetch_one=True)
    return result['unread_count'] if result else 0

# Forum Rooms operations
def create_forum_room(room_data: dict):
    query = """
    INSERT INTO forum_rooms (id, name, description, category, icon, is_private, rules, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    rules_str = json.dumps(room_data.get('rules', []))
    
    params = (
        room_data['id'],
        room_data['name'],
        room_data['description'],
        room_data['category'],
        room_data.get('icon', '💬'),
        room_data.get('is_private', False),
        rules_str,
        room_data['created_by']
    )
    return execute_query(query, params)

def get_forum_rooms(category: str = None, page: int = 1, limit: int = 20):
    query = "SELECT * FROM forum_rooms WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY last_activity DESC LIMIT %s OFFSET %s"
    params.extend([limit, (page - 1) * limit])
    
    return execute_query(query, tuple(params))

def get_forum_room_by_id(room_id: str):
    query = "SELECT * FROM forum_rooms WHERE id = %s"
    return execute_query(query, (room_id,), fetch_one=True)

def update_forum_room(room_id: str, update_data: dict):
    if not update_data:
        return None
    
    if 'rules' in update_data:
        update_data['rules'] = json.dumps(update_data['rules'])
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE forum_rooms SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (room_id,)
    return execute_query(query, params)

def update_room_activity(room_id: str):
    query = "UPDATE forum_rooms SET last_activity = CURRENT_TIMESTAMP WHERE id = %s"
    return execute_query(query, (room_id,))

# Room Members operations
def join_room(member_data: dict):
    query = """
    INSERT INTO forum_room_members (id, room_id, user_id, role)
    VALUES (%s, %s, %s, %s)
    """
    
    params = (
        member_data['id'],
        member_data['room_id'],
        member_data['user_id'],
        member_data.get('role', 'member')
    )
    
    result = execute_query(query, params)
    if result:
        # Update member count
        update_query = "UPDATE forum_rooms SET member_count = member_count + 1 WHERE id = %s"
        execute_query(update_query, (member_data['room_id'],))
    
    return result

def leave_room(room_id: str, user_id: str):
    query = "DELETE FROM forum_room_members WHERE room_id = %s AND user_id = %s"
    result = execute_query(query, (room_id, user_id))
    
    if result:
        # Update member count
        update_query = "UPDATE forum_rooms SET member_count = member_count - 1 WHERE id = %s"
        execute_query(update_query, (room_id,))
    
    return result

def is_room_member(room_id: str, user_id: str):
    query = "SELECT * FROM forum_room_members WHERE room_id = %s AND user_id = %s"
    return execute_query(query, (room_id, user_id), fetch_one=True)

def get_room_members(room_id: str, page: int = 1, limit: int = 50):
    query = """
    SELECT rm.*, u.name, u.avatar 
    FROM forum_room_members rm 
    JOIN users u ON rm.user_id = u.id 
    WHERE rm.room_id = %s 
    ORDER BY rm.joined_at DESC 
    LIMIT %s OFFSET %s
    """
    return execute_query(query, (room_id, limit, (page - 1) * limit))

# Forum Posts operations
def create_forum_post(post_data: dict):
    query = """
    INSERT INTO forum_posts (id, room_id, author_id, content, is_anonymous, mood, tags, attachments)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    tags_str = json.dumps(post_data.get('tags', []))
    attachments_str = json.dumps(post_data.get('attachments', []))
    
    params = (
        post_data['id'],
        post_data['room_id'],
        post_data['author_id'],
        post_data['content'],
        post_data.get('is_anonymous', False),
        post_data.get('mood'),
        tags_str,
        attachments_str
    )
    
    result = execute_query(query, params)
    if result:
        # Update room post count and activity
        update_room_query = """
        UPDATE forum_rooms 
        SET post_count = post_count + 1, last_activity = CURRENT_TIMESTAMP 
        WHERE id = %s
        """
        execute_query(update_room_query, (post_data['room_id'],))
    
    return result

def get_forum_posts(room_id: str, page: int = 1, limit: int = 20, sort: str = "newest"):
    query = """
    SELECT p.*, u.name as author_name, u.avatar as author_avatar 
    FROM forum_posts p 
    JOIN users u ON p.author_id = u.id 
    WHERE p.room_id = %s
    """
    
    if sort == "popular":
        query += " ORDER BY p.like_count DESC, p.comment_count DESC"
    else:  # newest
        query += " ORDER BY p.created_at DESC"
    
    query += " LIMIT %s OFFSET %s"
    return execute_query(query, (room_id, limit, (page - 1) * limit))

def get_forum_post_by_id(post_id: str):
    query = """
    SELECT p.*, u.name as author_name, u.avatar as author_avatar 
    FROM forum_posts p 
    JOIN users u ON p.author_id = u.id 
    WHERE p.id = %s
    """
    return execute_query(query, (post_id,), fetch_one=True)

def update_forum_post(post_id: str, update_data: dict):
    if not update_data:
        return None
    
    if 'tags' in update_data:
        update_data['tags'] = json.dumps(update_data['tags'])
    if 'attachments' in update_data:
        update_data['attachments'] = json.dumps(update_data['attachments'])
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE forum_posts SET {set_clause}, is_edited = TRUE, edited_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (post_id,)
    return execute_query(query, params)

def delete_forum_post(post_id: str):
    # Get room_id first for updating counts
    post_data = get_forum_post_by_id(post_id)
    if not post_data:
        return False
    
    query = "DELETE FROM forum_posts WHERE id = %s"
    result = execute_query(query, (post_id,))
    
    if result and post_data:
        # Update room post count
        update_query = "UPDATE forum_rooms SET post_count = post_count - 1 WHERE id = %s"
        execute_query(update_query, (post_data['room_id'],))
    
    return result

# Post Likes operations
def like_post(like_data: dict):
    query = """
    INSERT INTO forum_post_likes (id, post_id, user_id)
    VALUES (%s, %s, %s)
    """
    
    params = (like_data['id'], like_data['post_id'], like_data['user_id'])
    result = execute_query(query, params)
    
    if result:
        # Update post like count
        update_query = "UPDATE forum_posts SET like_count = like_count + 1 WHERE id = %s"
        execute_query(update_query, (like_data['post_id'],))
    
    return result

def unlike_post(post_id: str, user_id: str):
    query = "DELETE FROM forum_post_likes WHERE post_id = %s AND user_id = %s"
    result = execute_query(query, (post_id, user_id))
    
    if result:
        # Update post like count
        update_query = "UPDATE forum_posts SET like_count = like_count - 1 WHERE id = %s"
        execute_query(update_query, (post_id,))
    
    return result

def is_post_liked(post_id: str, user_id: str):
    query = "SELECT * FROM forum_post_likes WHERE post_id = %s AND user_id = %s"
    return execute_query(query, (post_id, user_id), fetch_one=True)

# Forum Comments operations
def create_forum_comment(comment_data: dict):
    query = """
    INSERT INTO forum_comments (id, post_id, author_id, content, is_anonymous)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    params = (
        comment_data['id'],
        comment_data['post_id'],
        comment_data['author_id'],
        comment_data['content'],
        comment_data.get('is_anonymous', False)
    )
    
    result = execute_query(query, params)
    if result:
        # Update post comment count
        update_query = "UPDATE forum_posts SET comment_count = comment_count + 1 WHERE id = %s"
        execute_query(update_query, (comment_data['post_id'],))
        
        # Update room activity
        post_data = get_forum_post_by_id(comment_data['post_id'])
        if post_data:
            update_room_activity(post_data['room_id'])
    
    return result

def get_forum_comments(post_id: str, page: int = 1, limit: int = 20):
    query = """
    SELECT c.*, u.name as author_name, u.avatar as author_avatar 
    FROM forum_comments c 
    JOIN users u ON c.author_id = u.id 
    WHERE c.post_id = %s 
    ORDER BY c.created_at ASC 
    LIMIT %s OFFSET %s
    """
    return execute_query(query, (post_id, limit, (page - 1) * limit))

def get_forum_comment_by_id(comment_id: str):
    query = """
    SELECT c.*, u.name as author_name, u.avatar as author_avatar 
    FROM forum_comments c 
    JOIN users u ON c.author_id = u.id 
    WHERE c.id = %s
    """
    return execute_query(query, (comment_id,), fetch_one=True)

def update_forum_comment(comment_id: str, update_data: dict):
    if not update_data:
        return None
    
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    query = f"UPDATE forum_comments SET {set_clause}, is_edited = TRUE, edited_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
    params = tuple(update_data.values()) + (comment_id,)
    return execute_query(query, params)

def delete_forum_comment(comment_id: str):
    # Get post_id first for updating counts
    comment_data = get_forum_comment_by_id(comment_id)
    if not comment_data:
        return False
    
    query = "DELETE FROM forum_comments WHERE id = %s"
    result = execute_query(query, (comment_id,))
    
    if result and comment_data:
        # Update post comment count
        update_query = "UPDATE forum_posts SET comment_count = comment_count - 1 WHERE id = %s"
        execute_query(update_query, (comment_data['post_id'],))
    
    return result

# Comment Likes operations
def like_comment(like_data: dict):
    query = """
    INSERT INTO forum_comment_likes (id, comment_id, user_id)
    VALUES (%s, %s, %s)
    """
    
    params = (like_data['id'], like_data['comment_id'], like_data['user_id'])
    result = execute_query(query, params)
    
    if result:
        # Update comment like count
        update_query = "UPDATE forum_comments SET like_count = like_count + 1 WHERE id = %s"
        execute_query(update_query, (like_data['comment_id'],))
    
    return result

def unlike_comment(comment_id: str, user_id: str):
    query = "DELETE FROM forum_comment_likes WHERE comment_id = %s AND user_id = %s"
    result = execute_query(query, (comment_id, user_id))
    
    if result:
        # Update comment like count
        update_query = "UPDATE forum_comments SET like_count = like_count - 1 WHERE id = %s"
        execute_query(update_query, (comment_id,))
    
    return result

def is_comment_liked(comment_id: str, user_id: str):
    query = "SELECT * FROM forum_comment_likes WHERE comment_id = %s AND user_id = %s"
    return execute_query(query, (comment_id, user_id), fetch_one=True)

# Reports operations
def create_forum_report(report_data: dict):
    query = """
    INSERT INTO forum_reports (id, post_id, comment_id, reporter_id, reason, description)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    params = (
        report_data['id'],
        report_data.get('post_id'),
        report_data.get('comment_id'),
        report_data['reporter_id'],
        report_data['reason'],
        report_data.get('description')
    )
    return execute_query(query, params)

def get_user_joined_rooms(user_id: str):
    query = """
    SELECT r.* 
    FROM forum_rooms r 
    JOIN forum_room_members rm ON r.id = rm.room_id 
    WHERE rm.user_id = %s 
    ORDER BY r.last_activity DESC
    """
    return execute_query(query, (user_id,))

def get_trending_posts(period: str = "week", limit: int = 10):
    if period == "day":
        date_filter = "DATE(created_at) = CURDATE()"
    elif period == "week":
        date_filter = "created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    else:  # month
        date_filter = "created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    
    query = f"""
    SELECT p.*, u.name as author_name, u.avatar as author_avatar, r.name as room_name
    FROM forum_posts p 
    JOIN users u ON p.author_id = u.id 
    JOIN forum_rooms r ON p.room_id = r.id 
    WHERE {date_filter}
    ORDER BY (p.like_count * 2 + p.comment_count) DESC 
    LIMIT %s
    """
    return execute_query(query, (limit,))