import streamlit as st
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