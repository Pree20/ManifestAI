from services.snowflake_db import get_snowflake_connection
from datetime import datetime

def get_next_conversation_id(user_id):
    conn = get_snowflake_connection(schema="chat")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT MAX(conversation_id) 
            FROM daily_chat 
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        max_id = result[0] if result[0] is not None else 0
        return max_id + 1
    except Exception as e:
        print("Error getting next conversation_id:", e)
        return 1
    finally:
        cursor.close()
        conn.close()

def log_chat_to_db(user_id, user_name, conversation_id, ai_question, user_response):
    try:
        
        conn = get_snowflake_connection(schema="chat")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
        print("📌 Connected to:", cursor.fetchone())
        now = datetime.now()
        recorded_date = now.date()
        recorded_time = now.time()
        created_at = now
        
        print("✅ Data prepared:")
        print("User:", user_name)
        print("Date:", recorded_date)
        print("Time:", recorded_time)
        print("AI:", ai_question)
        print("User Response:", user_response)
        print("Inserting chat to DB...")
        print("🧾 Final insert values:", user_id, user_name, recorded_date, recorded_time, ai_question, user_response,created_at)

        cursor.execute("""
            INSERT INTO DAILY_CHAT (user_id, user_name, conversation_id,recorded_date, recorded_time, ai_question, user_response,created_at)
            VALUES (%s, %s, %s,%s, %s, %s, %s,%s)
        """, (user_id, user_name,conversation_id,recorded_date, recorded_time, ai_question, user_response,created_at))
        conn.commit()
        print("Inserted chat to DB...")
    except Exception as e:
        import traceback
        print("Error logging chat:", e)
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


def get_user_conversations(user_id):
    conn = get_snowflake_connection(schema="CHAT")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT conversation_id, 
                   MIN(recorded_date || ' ' || recorded_time) AS start_time,
                   MAX(ai_question) AS last_ai_response,
                   MIN(created_at) AS earliest_message_time
            FROM daily_chat
            WHERE user_id = %s
            GROUP BY conversation_id
            ORDER BY earliest_message_time
        """, (user_id,))
        rows = cursor.fetchall()
        conversations = []
        for row in rows:
            conv_id, start_time, snippet, _ = row
            # Optional: Fetch chat history for each conversation
            cursor.execute("""
                SELECT user_response,ai_question FROM daily_chat 
                WHERE conversation_id = %s
                ORDER BY recorded_date, recorded_time
            """, (conv_id,))
            history = []
            welcome_message = "Hi there! Let's take a moment to check in. How are you feeling today?"
            history.append(("ai", welcome_message))
            for user_msg,ai_msg in cursor.fetchall():
                if user_msg:
                    history.append(("user", user_msg))
                if ai_msg:
                    history.append(("ai", ai_msg))
                
            conversations.append({
                "conversation_id": conv_id,
                "start_time": start_time,
                "snippet": (snippet or "No response yet")[:50] + "...",
                "history": history
            })
        return conversations
    except Exception as e:
        print("Error fetching conversations:", e)
        return []
    finally:
        cursor.close()
        conn.close()