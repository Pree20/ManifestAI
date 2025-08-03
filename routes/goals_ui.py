import streamlit as st
import requests
from services.goal_service import add_goal,load_goals, get_goal_by_id, add_reflection,get_reflections,save_goal_steps, get_goal_steps_from_db,save_step_progress
from services.llm_service import score_goal_progress, generate_steps_for_goal


API_BASE = "http://127.0.0.1:5000"

def show_goals_page():
    st.title("🎯 Your Goals")
    
    if "goals_mode" not in st.session_state:
        st.session_state.goals_mode = None

    try:
        res = requests.post(f"{API_BASE}/goals/all",json={"user_id":st.session_state.user_id})
        res.raise_for_status()
        goals = res.json().get("goals", [])
        print("📌 Goals received:", goals)
    except Exception as e:
        st.error("Failed to load goals.")
        st.stop()

    goals = load_goals(st.session_state.user_id)
    cols = st.columns(3)
    for i, (goal_id,goal_name) in enumerate(goals):
        col =cols[i%3]
        with col:
            if st.button(goal_name, key=goal_id):
                st.session_state.current_goal_id = goal_id
                st.session_state.current_goal_name = goal_name
                st.session_state.page = "🎯 Goals"
                st.experimental_rerun()

    if st.button("➕ Add New Goal"):
        st.session_state.goals_mode = "add"

    if st.session_state.goals_mode == "add":
        with st.form("add_goal_form", clear_on_submit=True):
            new_goal = st.text_input("Enter your new goal:")
            submitted = st.form_submit_button("Save Goal")

            if submitted and new_goal.strip():
                goal_id = add_goal(st.session_state.user_id, new_goal.strip())
                st.success("🎉 Goal added successfully!")
                steps = generate_steps_for_goal(new_goal.strip())
                # 3. Save steps
                print("goal steps generated successfully",steps)
                print("goal_id:",goal_id)
                save_goal_steps(st.session_state.user_id, goal_id, steps)
                st.success("Goal and steps added successfully!")
                
                st.session_state.goals_mode = None
                st.experimental_rerun()
    
    
    # --- Goal Grid ---
    #goals = load_goals()
  
    # for i, goal in enumerate(goals):
    #     with cols[i % 3]:
    #         if st.button(goal["text"], key=goal["id"]):
    #             st.session_state["current_goal_id"] = goal["id"]
    #             st.session_state["page"] = "goal_detail"
    #             st.experimental_rerun()

    st.markdown("---")

    # --- Add New Goal ---
    # with st.form("add_goal_form"):
    #     new_goal = st.text_input("Write a new goal")
    #     submitted = st.form_submit_button("Add Goal")
    #     if submitted and new_goal:
    #         add_goal(st.session_state.user_id,new_goal)
    #         st.experimental_rerun()
            
def show_goal_detail_page():
    import json
    import re
    import requests
    import streamlit as st

    goal_id = st.session_state.get("current_goal_id")
    goal_name = st.session_state.get("current_goal_name")
    user_id = st.session_state.user_id

    if not goal_id or not goal_name:
        st.warning("No goal selected.")
        return

    if st.button("🔙 Back to Goals"):
        st.session_state.page = "goals"
        st.session_state.pop("current_goal_id", None)
        st.session_state.pop("current_goal_name", None)
        st.experimental_rerun()

    st.header(f"📝 Reflections for: {goal_name}")

    # --- Fetch Steps ---
    try:
        res = requests.post(f"{API_BASE}/goals/steps", json={"user_id": user_id, "goal_id": goal_id})
        res.raise_for_status()
        goal_steps = res.json().get("steps", [])
        
    except Exception:
        st.error("Failed to load goal steps.")
        goal_steps = []

    st.subheader("📋 Steps for this Goal")
    if goal_steps:
        for step in goal_steps:
            description = step["description"]
            score = step.get("score", 0)
            checked = score >= 100

            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.checkbox(label=description, value=checked, key=f"chk_{step['step_id']}", disabled=True)
            with col2:
                st.markdown(f"**{score}%**")
    else:
        st.info("No steps found for this goal.")

    # --- Reflect on Selected Step ---
    st.markdown("---")
    print(goal_steps)
    if goal_steps:
        step_options = [f"{i+1}. {step['description']}" for i, step in enumerate(goal_steps)]
        selected_idx = st.selectbox("Choose a step to reflect on:", range(len(step_options)), format_func=lambda i: step_options[i])
        selected_step = goal_steps[selected_idx]
        selected_step_id = selected_step["step_id"]

        reflection_input = st.text_area("Reflect on this step", key="reflection_input")
        if st.button("Submit Reflection"):
            if not reflection_input.strip():
                st.warning("Please enter a reflection before submitting.")
            else:
                payload = {
                    "goal_id": goal_id,
                    "goal_text": goal_name,
                    "user_id": user_id,
                    "reflection": reflection_input,
                    "step_id": selected_step_id,
                    "steps": [s["description"] for s in goal_steps]
                }
                print(user_id,goal_id)
                res = requests.post(f"{API_BASE}/goals/reflect", json=payload)
                if res.status_code == 200:
                    ai_response = res.json().get("ai_response")
                    st.success("✅ Reflection saved and scored!")
                    st.markdown(f"**AI Feedback:**\n\n{ai_response}")
                else:
                    st.error("❌ Something went wrong saving your reflection.")

    # --- Past Reflections ---
    st.subheader("Past Reflections")
    for step in goal_steps:
        if isinstance(step.get("step_progress"), str):
            try:
                step["step_progress"] = json.loads(step["step_progress"])
            except json.JSONDecodeError:
                step["step_progress"] = []

    if selected_step.get("step_progress"):
        for entry in selected_step["step_progress"]:
            st.markdown(f"- **{entry['timestamp']}**: {entry['user_input']}")
            st.markdown(f"  - \U0001F9E0 {entry['ai_feedback']}")
    else:
        st.info("No reflections yet for this step.")
