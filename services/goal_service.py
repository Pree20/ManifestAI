import json
import os
import uuid

GOAL_FILE=r'E:\TherapyAI\data\user_goal.json'

def load_goals():
    if os.path.exists(GOAL_FILE):
        with open(GOAL_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
    return []


def save_goals(goals):
    with open(GOAL_FILE, "w") as f:
        json.dump(goals, f, indent=2)


def add_goal(goal_text):
    goals = load_goals()
    new_goal = {"id": str(uuid.uuid4()), "text": goal_text, "reflections": []}
    goals.append(new_goal)
    save_goals(goals)
    return new_goal


def get_goal_by_id(goal_id):
    goals = load_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            return goal
    return None


def add_reflection(goal_id, reflection):
    goals = load_goals()
    for goal in goals:
        if goal["id"] == goal_id:
            goal.setdefault("reflections", []).append(reflection)
            break
    save_goals(goals)

