import cohere
import os
from dotenv import load_dotenv
import requests
from flask import jsonify

load_dotenv()
co = cohere.Client(os.getenv('COHERE_API_KEY'))

API_BASE = "http://127.0.0.1:5000"

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

def score_goal_progress(user_input,goals,steps,step_id):
    prompt=(
        f"The user defined their goal progress for the following goal:{goals} as follows:{user_input}\n"
        "following are the steps for the goal:{steps} and they are reflecting on step_id {step_id}\n"
        "As a supportive, reflective coach, return two things:\n"
        "1. An estimated progress score (0 to 100%) based on the input.\n"
        "2. A short, encouraging message that validates their effort.\n\n"
        "Format the response like this:\n"
        "Progress: <score>%\nMessage: <feedback>"
    )
    response = co.chat(model='command-r-plus',message=prompt)
    return response.text

def generate_steps_for_goal(goal_text):
    prompt = (
        f"You are a helpful assistant. Suggest 3 to 5 actionable and sequential steps to achieve the goal: '{goal_text}'.\n"
        "Return the steps as a numbered list. Each step should start with the step number followed by a period and space.\n" \
        "Just start listing the steps out."
        "Example:\n"
        "1. First step here\n"
        "2. Second step here\n"
        "3. Third step here\n"
        "Now list the steps:"
    )
    response = co.chat(model='command-r-plus',message=prompt)
    raw_steps = response.text.strip()
    print(response)
    import re
    split_steps = re.split(r'\s*\d+\.\s*', raw_steps)
    structured_steps = []
    for i, step in enumerate(split_steps):
        step_text = step.strip()
        if step_text:  # Avoid empty strings
            structured_steps.append({
                "step_id": i,
                "description": step_text,
                "status": "Not Started"
            })
    return structured_steps

    #try:
    #     res = requests.post(f"{API_BASE}/generate_steps", json={"prompt": prompt})
    #     res.raise_for_status()
    #     steps = res.json().get("steps", [])

    #     # Optional: Structure steps with status
    #     structured_steps = [{"step_id": i + 1, "description": step, "status": "Not Started"} for i, step in enumerate(steps)]
    #     return structured_steps

    # except requests.exceptions.RequestException as e:
    #     print("Error generating steps:", e)
    #     return []