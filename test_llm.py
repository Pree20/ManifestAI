from llm import continue_chat, set_goal,get_goal,score_goal_progress


def interactive_session():
    print("🧠 TherapyAI - Daily Chat Session")
    print("AI: How was your day?\n")

    user_input = input("You: ")

    while True:
        if user_input.lower().strip() in ["exit", "quit"]:
            print("\n✨ End of session. Thank you for checking in!\n")
            break

        ai_response = continue_chat(user_input)
        print(f"\nAI: {ai_response}\n")
        #user_input = input("You: ")

        # Ask user what they want to do next
        next_action = input("🧭 Would you like to [continue] chatting or [goals] to reflect on your goals?\n> ").strip().lower()

        if next_action == "continue":
            user_input = input("\nYou: ")
        elif next_action == "goals":
            print("\n🎯 What would you like to do?")
            print("[set] Set a new goal")
            print("[reflect] Reflect on your current goal")
            goal_action = input("> ").strip().lower()

            if goal_action == "set":
                new_goal = input("\nWhat's your new goal?\nYou: ")
                confirmation = set_goal(new_goal)
                print(f"\n✅ {confirmation}")
                break

            elif goal_action == "reflect":
                current_goal = get_goal()
                print(f"\n📌 Your current goal is: {current_goal}")
                goal_input = input("How did you do with your goal today?\nYou: ")
                goal_response = score_goal_progress(goal_input)
                print(f"\n🏁 AI Goal Feedback:\n{goal_response}")
                break

            else:
                print("❗Please type 'set' or 'reflect'. Returning to main menu...\n")

if __name__ == "__main__":
    interactive_session()
