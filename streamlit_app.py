import streamlit as st
from services.goal_service import load_goals, add_goal, get_goal_by_id, add_reflection
from services.llm_service import score_goal_progress
from routes.chat_ui import show_daily_reflection_page
from routes.goals_ui import show_goals_page, show_goal_detail_page
from routes.auth_ui import show_login_page


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
