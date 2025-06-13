from flask import Blueprint, request, jsonify
from services.llm_service import continue_chat,format_history_for_prompt

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data=request.json
    user_input = data.get("message")
    history = data.get("history", [])
    history_text = format_history_for_prompt(history)
    response = continue_chat(history_text,user_input)
    return jsonify({"response": response})
