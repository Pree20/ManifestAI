from flask import Flask
from routes.chat_api import chat_bp
from routes.goals_api import goals_bp

app = Flask(__name__)
app.register_blueprint(chat_bp)
app.register_blueprint(goals_bp)

if __name__ == "__main__":
    app.run(debug=True)
