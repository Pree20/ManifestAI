from flask import Blueprint, request, jsonify
from services.llm_service import continue_chat

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = continue_chat(user_input)
    return jsonify({"response": response})
