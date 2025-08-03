import json
import os
import uuid
from .snowflake_db import get_snowflake_connection
from datetime import datetime

GOAL_FILE = os.path.join("data", "user_goal.json")

def load_goals(user_id):
    # if os.path.exists(GOAL_FILE):
    #     with open(GOAL_FILE, "r") as f:
    #         try:
    #             data = json.load(f)
    #             if isinstance(data, list):
    #                 return data
    #         except json.JSONDecodeError:
    #             pass
    # return []
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT goal_id, goal_name FROM goal_info WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching goals:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def add_goal(user_id, goals):
    # with open(GOAL_FILE, "w") as f:
    #     json.dump(goals, f, indent=2)
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    created_at = datetime.now()
    try:
        cursor.execute("insert into goal_info (user_id,goal_name,created_at) values (%s,%s,%s)",(user_id,goals,created_at))
        conn.commit()
        cursor.execute("""
            SELECT goal_id FROM goal_info
            WHERE user_id = %s AND goal_name = %s AND created_at = %s
            ORDER BY goal_id DESC
            LIMIT 1
        """, (user_id, goals, created_at))
        result = cursor.fetchone()
        goal_id = result[0] if result else None
        print(f"goal_id: {goal_id} for '{goals}' saved!")
        conn.commit()
        return goal_id
        
    except Exception as e:
        print("Error saving goal:", e)
    finally:
        cursor.close()
        conn.close()


# def add_goal(goal_text):
#     goals = load_goals()
#     new_goal = {"id": str(uuid.uuid4()), "text": goal_text, "reflections": []}
#     goals.append(new_goal)
#     save_goals(goals)
#     return new_goal


def get_goal_by_id(user_id,goal_id):
    # goals = load_goals()
    # for goal in goals:
    #     if goal["id"] == goal_id:
    #         return goal
    # return None
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        cursor.execute("select goal_id,goal_name from goals_info where goal_id=%s and user_id = %s",(goal_id,user_id))
        result = cursor.fetchnone()
        if result:
            return {"id": result[0], "text": result[1]}
    except Exception as e:
        print("Error fetching goal by ID:", e)
    finally:
        cursor.close()
        conn.close()
    return None


def add_reflection(user_id,goal_id, reflection,ai_feedback):
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        #created_at=datetime.now()
        cursor.execute("""
            INSERT INTO goal_reflections (user_id,goal_id, reflection,ai_feedback, created_at)
            VALUES (%s,%s, %s,%s, CURRENT_TIMESTAMP)
        """, (user_id,goal_id, reflection,ai_feedback))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_reflections(user_id,goal_id):
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT reflection, created_at,ai_feedback
            FROM goal_reflections
            WHERE user_id= %s and goal_id = %s
            ORDER BY created_at DESC
        """, (user_id,goal_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def save_goal_steps(user_id, goal_id, steps):
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        for step in steps:
            step_id = step['step_id']
            description = step["description"]
            step_progress = json.dumps([])  # empty array as JSON string
            created_at = datetime.now()

            insert_query = """
            INSERT INTO MANIFESTAI.GOALS.GOAL_STEPS (
                user_id, goal_id, step_id, step_description, step_progress, created_at
            )
            SELECT %s, %s, %s, %s, PARSE_JSON(%s), %s
            """
            cursor.execute(insert_query, (
                user_id,
                goal_id,
                step_id,
                description,
                step_progress,
                created_at
            ))

        conn.commit()
        print("✅ Goal steps saved for user_id =", user_id, "goal_id =", goal_id)
    except Exception as e:
        print("Error saving goal steps:", e)
    finally:
        cursor.close()
        conn.close()


def get_goal_steps_from_db(user_id, goal_id):
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT step_id,step_description,step_progress,progress FROM goal_steps
            WHERE user_id = %s AND goal_id = %s
            ORDER BY STEP_ID
        """, (user_id, goal_id))
        rows = cursor.fetchall()
        steps=[]
        for row in rows:
            step_id, description, progress, score = row
            steps.append({
                "step_id": step_id,
                "description": description,
                "step_progress": progress,
                "score": score if score is not None else 0
            })
        print("Goal steps fetched from DB:", steps)
        return steps
    finally:
        cursor.close()
        conn.close()

def save_step_progress(user_id, goal_id, step_id, reflection, ai_response):
    conn = get_snowflake_connection(schema="goals")
    cursor = conn.cursor()
    try:
        # Step 1: Get existing step_progress
        cursor.execute(
            "SELECT step_progress FROM goal_steps WHERE user_id = %s AND goal_id = %s AND step_id = %s",
            (user_id, goal_id, step_id)
        )
        result = cursor.fetchone()
        existing_progress = json.loads(result[0]) if result and result[0] else []

        # Step 2: Extract score from ai_response
        import re
        match = re.search(r"Progress:\s*(\d+)%", ai_response)
        score = int(match.group(1)) if match else 0

        # Step 3: Append new progress entry
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": reflection,
            "ai_feedback": ai_response,
            "score": score
        }
        existing_progress.append(new_entry)

        # Step 4: Save back to DB (including score)
        cursor.execute(
            "UPDATE goal_steps SET step_progress = %s, progress = %s WHERE user_id = %s AND goal_id = %s AND step_id = %s",
            (json.dumps(existing_progress), score, user_id, goal_id, step_id)
        )
        conn.commit()
    except Exception as e:
        print("Error appending new progress", e)
    finally:
        cursor.close()
        conn.close()
