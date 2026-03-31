"""
app.py - The Heart of the Backend
==================================
This is the main Flask application file. Flask is a lightweight Python web
framework that lets us create API endpoints — essentially URLs that our
frontend can talk to. Think of this file as the "brain" that receives messages
from the chat interface, decides what to ask next, and eventually calls the
AI to generate a resume.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from resume_generator import generate_resume
from conversation import ConversationManager

# --- App Initialization ---
# Flask(__name__) creates a new Flask app. __name__ tells Flask where to find
# resources relative to this file.
app = Flask(__name__)

# SECRET_KEY is required by Flask to securely sign session cookies.
# In production, use a long random string stored in an environment variable.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# CORS (Cross-Origin Resource Sharing) allows our frontend (on a different
# port or domain) to talk to this backend. Without this, browsers block
# requests for security reasons.
CORS(app, supports_credentials=True)


# --- In-Memory Session Store ---
# For simplicity, we store conversation state in a dictionary keyed by
# session ID. In production, you'd use Redis or a database.
# Structure: { session_id: { "step": int, "data": {...} } }
conversations = {}


@app.route("/", methods=["GET"])
def health_check():
    """
    Simple health check endpoint.
    Visiting http://localhost:5000/ confirms the server is running.
    """
    return jsonify({"status": "ok", "message": "AI Resume Builder API is running!"})


@app.route("/chat", methods=["POST"])
def chat():
    """
    /chat — The Main Endpoint
    --------------------------
    This is the only endpoint the frontend talks to. It receives a JSON body
    like: { "message": "John Doe", "session_id": "abc123" }

    It:
    1. Reads the user's message and session ID
    2. Looks up (or creates) the conversation state for that session
    3. Passes the message to ConversationManager to figure out the next step
    4. Returns the bot's response as JSON
    """
    # Parse the incoming JSON body
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    # --- Validation: Don't accept empty messages ---
    if not user_message:
        return jsonify({
            "reply": "I didn't catch that — please type something!",
            "step": conversations.get(session_id, {}).get("step", 0),
            "done": False
        })

    # --- Get or create conversation state ---
    if session_id not in conversations:
        conversations[session_id] = {
            "step": 0,          # Which question we're on (0 = just started)
            "data": {}          # Collected user data so far
        }

    conv = conversations[session_id]
    manager = ConversationManager(conv["step"], conv["data"])

    # --- Process the message and get a response ---
    reply, next_step, collected_data, is_done = manager.process(user_message)

    # --- Update stored state ---
    conversations[session_id]["step"] = next_step
    conversations[session_id]["data"] = collected_data

    # --- If all data is collected, generate the resume ---
    resume_text = None
    if is_done:
        resume_text = generate_resume(collected_data)
        # Clear session after resume is generated
        del conversations[session_id]

    return jsonify({
        "reply": reply,
        "step": next_step,
        "done": is_done,
        "resume": resume_text
    })


@app.route("/reset", methods=["POST"])
def reset():
    """
    /reset — Clear the Conversation
    ---------------------------------
    Lets the frontend start a fresh chat session by deleting stored state.
    """
    data = request.get_json()
    session_id = data.get("session_id", "default")

    if session_id in conversations:
        del conversations[session_id]

    return jsonify({"status": "reset", "message": "Conversation cleared. Let's start fresh!"})


if __name__ == "__main__":
    # debug=True enables hot-reloading and detailed error pages during development.
    # NEVER use debug=True in production.
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
