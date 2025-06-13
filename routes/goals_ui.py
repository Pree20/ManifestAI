import streamlit as st
from services.goal_service import load_goals, add_goal, get_goal_by_id, add_reflection
from services.llm_service import score_goal_progress

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
