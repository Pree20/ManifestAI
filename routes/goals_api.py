from flask import Blueprint, request, jsonify
from services.goal_service import add_goal, load_goals
from services.llm_service import score_goal_progress

goals_bp = Blueprint('goals', __name__)

@goals_bp.route("/goals/add", methods=["POST"])
def add_user_goal():
    goal_text = request.json.get("goal")
    new_goal = add_goal(goal_text)
    return jsonify({"message": "Goal added!", "goal": new_goal})

@goals_bp.route("/goals/all", methods=["GET"])
def get_all_goals():
    goals = load_goals()
    return jsonify({"goals": goals})

@goals_bp.route("/goals/reflect", methods=["POST"])
def reflect_on_goal():
    progress_text = request.json.get("progress")
    result = score_goal_progress(progress_text)
    return jsonify({"reflection": result})
