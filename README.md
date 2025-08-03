# ManifestAI  
_A productivity tool that keeps you accountable through AI-powered check-ins, goal tracking, and progress monitoring._

## Overview
ManifestAI is a passion project designed to help users set goals, track their progress, and reflect daily with the support of an AI assistant.  
The tool ensures accountability by integrating **daily check-ins, actionable goal steps, and secure data storage** in a clean, intuitive interface.

## Features
-  **Secure Login/Signup**  
  - Access control ensures only logged-in users can view personalized data.
-  **AI-Powered Conversations**  
  - Start a new session or continue past ones with maintained context.  
-  **Goal Tracking**  
  - Add goals and auto-generate actionable steps.  
-  **Step-Level Reflections**  
  - Reflect on each step individually, with AI feedback and scoring.
-  **Progress Monitoring**  
  - Track progress over time with scores and stored reflections.
-  **Cloud Database Integration**  
  - All user data stored securely in Snowflake.

---

## Tech Stack
- **Backend:** Python (Flask)
- **Frontend:** Streamlit
- **Database:** Snowflake
- **AI Integration:** Cohere API
- **Testing:** Postman

---

ManifestAI/
│
├── app.py # Flask application entry point
├── streamlit_app.py # Streamlit frontend entry point
├── requirements.txt # Project dependencies
├── .env # Environment variables (not committed)
├── .gitignore # Git ignore file
│
├── data/ # Temporary JSON storage (before DB integration)
│ ├── users.json
│ └── user_goal.json
│
├── routes/ # API endpoints & UI routes
│ ├── auth_ui.py # Login/Signup UI
│ ├── chat_api.py # Chat-related API endpoints
│ ├── chat_ui.py # Chat UI
│ ├── goals_api.py # Goals-related API endpoints
│ └── goals_ui.py # Goals UI
│
├── services/ # Business logic & database integration
│ ├── chat_logger.py # Logs chat conversations
│ ├── goal_service.py # Handles goal creation & management
│ ├── llm_service.py # Cohere API integration for AI feedback
│ ├── snowflake_db.py # Snowflake database connection & queries
│ └── user_service.py # User authentication & management
│
└── README.md # Project documentation


Medium Article (Project Journey): https://pv20012000.medium.com/manifestai-a-productivity-tool-that-keeps-you-accountable-b505f221e106
Watch Video Here: https://youtu.be/5UZXnkGGyNQ
