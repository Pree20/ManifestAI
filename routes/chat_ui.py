import streamlit as st
import requests
from services.chat_logger import get_user_conversations,get_next_conversation_id
import uuid

API_BASE = "http://127.0.0.1:5000"

def show_chat_history():
    for speaker, msg in st.session_state.chat_history:
        if speaker == "user":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"🧠 **AI:** {msg}")

def show_input_form():
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", key="chat_input_{st.session_state.conversation_id}")
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


def show_chat_session():
    chat_container = st.container()
    with chat_container:
        for speaker, msg in st.session_state.chat_history:
            if speaker == "user":
                st.markdown(f"**You:** {msg}")
            else:
                st.markdown(f"🧠 **AI:** {msg}")

    if st.session_state.get("show_input", False):
        with st.form(f"chat_form_{st.session_state.conversation_id}", clear_on_submit=True):
            user_input = st.text_input("You:", key="chat_input")
            submitted = st.form_submit_button("Send")
            if submitted and user_input:
                st.session_state.chat_history.append(("user", user_input))

                res = requests.post(f"{API_BASE}/chat", json={
                    "user_id": st.session_state.user_id,
                    "user_name": st.session_state.username,
                    "message": user_input,
                    "history": st.session_state.chat_history,
                    "conversation_id": st.session_state.conversation_id  # <-- if needed
                })

                ai_msg = res.json()["response"]
                st.session_state.chat_history.append(("ai", ai_msg))
        

    if st.button("🔙 Return to Main Menu"):
        st.session_state.chat_mode = None
        st.session_state.chat_history = []
        st.session_state.show_input = False
        st.session_state.conversation_id = None
        #st.session_state.continue_chat = False
        st.experimental_rerun() 

def show_daily_reflection_page():
    st.title("🧠 ManifestAI - Daily Reflection")

    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = None
        st.session_state.show_input = False

    if st.session_state.chat_mode is None:
        st.subheader("What would you like to do?")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🆕 Start New Chat"):
                st.session_state.chat_mode = "new"
                st.session_state.conversation_id = get_next_conversation_id(st.session_state.user_id)
                st.session_state.chat_history = []
                st.session_state.show_input = True
                st.experimental_rerun()
                #show_chat_session()
        
        with col2:
            if st.button("📂 Continue Old Chat"):
                st.session_state.chat_mode = "resume"
                #conversations = get_user_conversations(st.session_state.user_id)
                st.session_state.show_input = False
                st.experimental_rerun()
        return #makes sure that nothing is rendered
        #Render based on mode 

    if st.session_state.chat_mode == "new":
        show_chat_session()
        # ai_reply = show_input_form()
        # if ai_reply:
        #     st.markdown(f"🧠 **AI:** {ai_reply}")
        # if not st.session_state.show_input and st.session_state.chat_history:
        #     show_followup_buttons()

    elif st.session_state.chat_mode == "resume":
        conversations = get_user_conversations(st.session_state.user_id)

        if not conversations:
            st.info("No previous conversations found.")
            st.session_state.chat_mode = None  # reset mode
            return
        
        selected = st.radio(
            "Select a past conversation:",
            [f"{c['start_time']} | {c['snippet']}" for c in conversations],
            index=0
        )

        if st.button("🔄 Resume Selected Chat"):
            selected_index = [f"{c['start_time']} | {c['snippet']}" for c in conversations].index(selected)
            selected_conv = conversations[selected_index]
            st.session_state.conversation_id = selected_conv["conversation_id"]
            st.session_state.chat_history = selected_conv["history"]
            st.session_state.show_input = False  # Prevent sending more messages
            st.session_state.chat_mode = "view_only"
            st.experimental_rerun()
            #show_chat_session()
    
    elif st.session_state.chat_mode == "view_only":
        show_chat_session()

        if st.button("💬 Continue this Conversation"):
            st.session_state.chat_mode = "continue_existing"
            st.session_state.show_input = True
            st.experimental_rerun()
    
    elif st.session_state.chat_mode == "continue_existing":
        show_chat_session()

    # show_chat_history()
    # ai_reply=None

    # if st.session_state.show_input:
    #     ai_reply = show_input_form()

    # if ai_reply:
    #     st.markdown(f"🧠 **AI:** {ai_reply}")

    # if not st.session_state.show_input and st.session_state.chat_history:
    #     show_followup_buttons()

    
    