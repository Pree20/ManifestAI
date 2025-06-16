from flask import Blueprint, request, jsonify
from services.llm_service import continue_chat,format_history_for_prompt
from services.chat_logger import log_chat_to_db

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data=request.json
        user_id = data.get("user_id")
        user_name = data.get("user_name")
        message = data.get("message")
        history = data.get("history", "")
        history_text = format_history_for_prompt(history)
        response = continue_chat(history_text,message)

        log_chat_to_db(user_id, user_name, ai_question=response, user_response=message)
        
        return jsonify({"response": response})
    except Exception as e:
        print("Error in /chat:", e)
        return jsonify({"error": str(e)}), 500
