import uuid
from services.snowflake_db import get_snowflake_connection
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_in_db(username, password):
    conn = get_snowflake_connection(schema="USERS")
    cursor = conn.cursor()
    print("connection string:",conn)
    try:
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
        print("📍 Connected to:", cursor.fetchone())
        #user_id = str(uuid.uuid4())
        cursor.execute("SELECT COUNT(*) FROM user_info WHERE user_name = %s", (username,))
        if cursor.fetchone()[0] > 0:
            print("❌ Username already exists!")
            return False
        hashed_pw = hash_password(password)
        print(username,password,hashed_pw)
        cursor.execute(
        "INSERT INTO user_info (user_name,password) VALUES (%s,%s)",
        (username,hashed_pw)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Error creating user:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def authenticate_user_from_db(username,password):
    conn = get_snowflake_connection(schema="USERS")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM user_info WHERE user_name = %s", (username))
        result = cursor.fetchone()
        if result:
            stored_hash = result[0]
            return stored_hash == hash_password(password)
        return False
    except Exception as e:
        print("Error authenticating user:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_id(username):
    conn = get_snowflake_connection(schema="USERS")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM user_info WHERE user_name = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()
