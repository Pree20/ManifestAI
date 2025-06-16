from services.snowflake_db import get_snowflake_connection
from datetime import datetime

def log_chat_to_db(user_id, user_name, ai_question, user_response):
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
            INSERT INTO DAILY_CHAT (user_id, user_name, recorded_date, recorded_time, ai_question, user_response,created_at)
            VALUES (%s, %s, %s, %s, %s, %s,%s)
        """, (user_id, user_name, recorded_date, recorded_time, ai_question, user_response,created_at))
        conn.commit()
        print("Inserted chat to DB...")
    except Exception as e:
        import traceback
        print("Error logging chat:", e)
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()
