from flask import Blueprint, request, jsonify
from services.goal_service import add_goal, load_goals,add_reflection,get_goal_steps_from_db,save_goal_steps,save_step_progress
from services.llm_service import score_goal_progress,generate_steps_for_goal

goals_bp = Blueprint('goals', __name__)

@goals_bp.route("/goals/add", methods=["GET"])
def add_user_goal():
    data = request.json
    goal_text = data.get("goal")
    user_id = data.get("user_id")
    new_goal = add_goal(user_id, goal_text)
    return jsonify({"message": "Goal added!", "goal": new_goal})

@goals_bp.route("/goals/all", methods=["POST"])
def get_all_goals():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    goals = load_goals(user_id)
    print(goals)
    return jsonify({"goals": goals})

@goals_bp.route("/goals/reflect", methods=["POST"])
def reflect_on_goal():
    data = request.get_json()

    # Extract all required fields from the POST body
    goal_id = data.get("goal_id")
    user_input = data.get("reflection")
    step_id = data.get("step_id")
    steps = data.get("steps")
    goal_text = data.get("goal_text")
    user_id = data.get("user_id")

    if not all([goal_id, user_input, step_id, steps, goal_text, user_id]):
        return jsonify({"error": "Missing one or more required fields"}), 400

    # Call scoring function
    ai_response = score_goal_progress(user_input, goal_text, steps, step_id)

    import re
    match = re.search(r"Progress:\s*(\d+)%", ai_response)
    score = int(match.group(1)) if match else 0

    # Optional: Save the reflection in your DB
    try:
        save_step_progress(user_id, goal_id, step_id, user_input, ai_response)
    except Exception as e:
        print("Error saving step reflection:", e)
        return jsonify({"error": "Failed to save reflection"}), 500

    return jsonify({
    "ai_response": ai_response,
    "score": score
    }), 200


@goals_bp.route("/goals/steps", methods=["POST"])
def get_goal_steps():
    data = request.get_json()
    user_id = data.get("user_id")
    goal_id = data.get("goal_id")

    if not user_id or not goal_id:
        return jsonify({"error": "Missing user_id or goal_id"}), 400

    try:
        steps = get_goal_steps_from_db(user_id, goal_id)
        print(steps)
        return jsonify({"steps": steps})
    except Exception as e:
        print("Error fetching goal steps:", e)
        return jsonify({"error": str(e)}), 500

# @goals_bp.route("/generate_steps", methods=["POST"])
# def generate_steps():
#     data = request.get_json()
#     goal_text = data.get("prompt")
#     if not goal_text:
#         return jsonify({"error": "Missing goal text"}), 400

#     steps = generate_steps_for_goal(goal_text)
#     return jsonify({"steps": steps})