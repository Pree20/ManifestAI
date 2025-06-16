import streamlit as st
import requests

API_BASE = "http://127.0.0.1:5000"

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

            try:
                res = requests.post(f"{API_BASE}/chat", json={
                    "user_id": st.session_state.user_id,
                    "user_name": st.session_state.username,
                    "message": user_input,
                    "history": st.session_state.chat_history
                })

                res.raise_for_status()  # raises error for non-2xx responses

                ai_msg = res.json()["response"]
                st.session_state.chat_history.append(("ai", ai_msg))
                st.session_state.show_input = False
                return ai_msg

            except requests.exceptions.RequestException as e:
                st.error("🚫 Failed to connect to the chat server.")
                st.warning(f"Details: {e}")
            except ValueError:
                st.error("⚠️ Received an invalid JSON response from the server.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


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
    st.title("🧠 ManifestAI - Daily Reflection")

    show_chat_history()

    ai_reply = None
    if st.session_state.show_input:
        ai_reply = show_input_form()

    if ai_reply:
        st.markdown(f"🧠 **AI:** {ai_reply}")

    if not st.session_state.show_input and st.session_state.chat_history:
        show_followup_buttons()