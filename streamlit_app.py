import streamlit as st
import requests
from services.goal_service import load_goals, add_goal, get_goal_by_id, add_reflection
from services.llm_service import score_goal_progress
import json
import hashlib
import os

USERS_FILE = os.path.join("data", "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username] == hash_password(password):
        return True
    return False

def create_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

API_BASE = "http://127.0.0.1:5000"

st.set_page_config(page_title="ManifestAI", layout="centered")

if "view" not in st.session_state:
    st.session_state["view"] = "list"

if "page" not in st.session_state:
    st.session_state["page"] = "🧠 Daily Reflection"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.sidebar.title("🧭 Navigate")
if st.session_state.logged_in:
    st.sidebar.write(f"👋 Logged in as **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "Login / Signup"
        st.experimental_rerun()
    page = st.sidebar.radio("Go to", ["🧠 Daily Reflection", "🎯 Goals"])
else:
    page = st.sidebar.radio("Go to", ["Login / Signup", "🧠 Daily Reflection", "🎯 Goals"])

st.session_state["page"] = page


# ---------- Session State Init ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_input" not in st.session_state:
    st.session_state.show_input = True

if not st.session_state.chat_history:
    # Inject initial system prompt (therapist-style opener)
    st.session_state.chat_history.append(
        ("ai", "Hi there! Let's take a moment to check in. How are you feeling today?")
    )


# ---------- Modular Functions ----------

def show_chat_history():
    for speaker, msg in st.session_state.chat_history:
        if speaker == "user":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"🧠 **AI:** {msg}")


def show_input_form():
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_input:
            st.session_state.chat_history.append(("user", user_input))
            res = requests.post(f"{API_BASE}/chat", json={"message": user_input,"history": st.session_state.chat_history})
            ai_msg = res.json()["response"]
            st.session_state.chat_history.append(("ai", ai_msg))
            st.session_state.show_input = False
            return ai_msg


def show_followup_buttons():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Continue"):
            st.session_state.show_input = True
    with col2:
        if st.button("❌ Exit"):
            st.success("Thank you for checking in today. See you again soon! 💜")
            st.session_state.chat_history.clear()
            st.session_state.show_input = False


def show_daily_reflection_page():
    st.title("🧠 TherapyAI - Daily Reflection")

    show_chat_history()

    ai_reply = None
    if st.session_state.show_input:
        ai_reply = show_input_form()

    if ai_reply:
        st.markdown(f"🧠 **AI:** {ai_reply}")

    if not st.session_state.show_input and st.session_state.chat_history:
        show_followup_buttons()

# --- 2. Goal Management ---
#st.set_page_config(page_title="TherapyAI Goals", layout="wide")


def show_goals_page():
    st.title("🎯 Your Goals")

    # --- Goal Grid ---
    goals = load_goals()
    cols = st.columns(3)

    for i, goal in enumerate(goals):
        with cols[i % 3]:
            if st.button(goal["text"], key=goal["id"]):
                st.session_state["current_goal_id"] = goal["id"]
                st.session_state["page"] = "goal_detail"
                st.experimental_rerun()

    st.markdown("---")

    # --- Add New Goal ---
    with st.form("add_goal_form"):
        new_goal = st.text_input("Write a new goal")
        submitted = st.form_submit_button("Add Goal")
        if submitted and new_goal:
            add_goal(new_goal)
            st.experimental_rerun()


def show_goal_detail_page():
    goal_id = st.session_state.get("current_goal_id")
    if not goal_id:
        st.warning("No goal selected.")
        return

    # --- Back Button ---
    if st.button("🔙 Back to Goals"):
        st.session_state["view"] = "list"
        st.session_state.pop("current_goal_id", None)
        st.experimental_rerun()

    goal = get_goal_by_id(goal_id)
    if not goal:
        st.error("Goal not found.")
        return

    st.header(f"📝 Reflections for: {goal['text']}")

    st.subheader("Past Reflections")
    for r in reversed(goal.get("reflections", [])):
        st.markdown(f"- {r}")

    st.markdown("---")
    with st.form("reflect_form"):
        reflection = st.text_area("How are you progressing with this goal?")
        submitted = st.form_submit_button("Submit Reflection")
        if submitted and reflection:
            feedback = score_goal_progress(reflection)
            add_reflection(goal_id, reflection)
            st.success(f"💬 AI Feedback: {feedback}")

def show_login_page():
    st.title("🔐 Login or Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "🧠 Daily Reflection"
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Create Account")
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if create_user(new_user, new_pass):
                st.success("Account created! You can log in now.")
            else:
                st.error("Username already exists")

# --- Page Router ---
if not st.session_state.logged_in and page != "Login / Signup":
    st.warning("You must log in to access this page.")
    show_login_page()
elif page == "Login / Signup":
    show_login_page()
elif page == "🧠 Daily Reflection":
    show_daily_reflection_page()
elif page == "🎯 Goals":
    if "current_goal_id" in st.session_state:
        show_goal_detail_page()
    else:
        show_goals_page()
