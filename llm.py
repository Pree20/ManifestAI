import cohere
import os
from dotenv import load_dotenv
import json
import os


CO_API_KEY = '0r65zLKTfTxxd9tZhtGPn92la8bMhmsfF7K8uGfu'
load_dotenv()
co = cohere.Client('0r65zLKTfTxxd9tZhtGPn92la8bMhmsfF7K8uGfu')

# Function to get a therapist-style follow-up based on user input
def continue_chat(user_input):
    prompt = (
        f"The user said: '{user_input}'. "
        "As a compassionate, emotionally intelligent AI therapist, your response should have two parts:\n"
        "1. A warm, validating reflection that shows understanding and support.\n"
        "2. A gentle follow-up question that invites the user to explore their feelings or situation more deeply.\n\n"
        "Avoid being too clinical or generic — speak with care, like a trusted friend who listens deeply."
    )
    response = co.chat(
        model="command-r-plus",
        message=prompt
    )
    return response.text

#Goal file
GOAL_FILE = "user_goal.json"

def set_goal(goal_text):
    goal_data = {"goal": goal_text}
    with open(GOAL_FILE, "w") as f:
        json.dump(goal_data, f)

    return f"Got it! I'll check in with you about: \"{goal_text}\" in future sessions."

def get_goal():
    if os.path.exists(GOAL_FILE):
        with open(GOAL_FILE, "r") as f:
            data = json.load(f)
            return data.get("goal", "No goal found.")
    else:
        return "No goal found."


def score_goal_progress(user_goal_input):
    prompt = (
        f"The user described their goal progress as: '{user_goal_input}'.\n"
        "As a supportive, reflective coach, return two things:\n"
        "1. An estimated progress score (0 to 100%) based on the input.\n"
        "2. A short, encouraging message that validates their effort.\n\n"
        "Format the response like this:\n"
        "Progress: <score>%\nMessage: <feedback>"
    )

    response = co.chat(
        model="command-r-plus",
        message=prompt
    )
    return response.text