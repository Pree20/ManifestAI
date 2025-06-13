import cohere
import os
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv('COHERE_API_KEY'))

def format_history_for_prompt(history):
    context = ""
    for speaker, message in history:
        prefix = "User:" if speaker == "user" else "AI:"
        context += f"{prefix} {message}\n"
    return context

def continue_chat(history_text, user_input):
    prompt = (
        f"so far the user has said this{history_text}, and now the user said:{user_input}"
        "As a compassionate, emotionally intelligent AI therapist, your response should have two parts:\n"
        "1. A warm, validating reflection that shows understanding and support.\n"
        "2. A gentle follow-up question that invites the user to explore their feelings or situation more deeply.\n\n"
        "Avoid being too clinical or generic — speak with care, like a trusted friend who listens deeply."
    )
    response = co.chat(model='command-r-plus',message=prompt)
    return response.text

def score_goal_progress(user_input):
    prompt=(
        f"The user defined their goal progress as follows:{user_input}"
        "As a supportive, reflective coach, return two things:\n"
        "1. An estimated progress score (0 to 100%) based on the input.\n"
        "2. A short, encouraging message that validates their effort.\n\n"
        "Format the response like this:\n"
        "Progress: <score>%\nMessage: <feedback>"
    )
    response = co.chat(model='command-r-plus',message=prompt)
    return response.text
