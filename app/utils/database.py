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