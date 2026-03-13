```python
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)

# -----------------------------
# Uploads config
# -----------------------------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# OpenRouter API config
# -----------------------------
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# -----------------------------
# Chat storage & JOM personality
# -----------------------------
messages = []

JOM_PROMPT = """
You are JOM.
Friendly Assistant 🙂
Professional Expert 🧑‍💼
Teacher / Tutor 👨‍🏫
Creative Writer ✍️
Always respond as JOM, friendly and helpful.
"""

# -----------------------------
# Helper functions
# -----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["jpg", "jpeg", "png"]

def jom_ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": JOM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        resp = requests.post(OPENROUTER_URL, json=data, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"JOM says: Sorry, AI is not available. ({str(e)})"

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/messages")
def get_messages():
    return jsonify(messages)

@app.route("/chat", methods=["POST"])
def chat():
    username = request.form.get("username")
    message = request.form.get("message")
    file = request.files.get("file")
    timestamp = datetime.now().strftime("%H:%M")

    file_url = None
    file_type = None

    if file and file.filename != "":
        filename = f"{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        file_url = f"/uploads/{filename}"
        ext = filename.split(".")[-1].lower()
        file_type = "image" if ext in ["jpg", "jpeg", "png"] else "file"

    if message or file_url:
        msg_data = {
            "username": username,
            "message": message,
            "timestamp": timestamp,
            "file_url": file_url,
            "file_type": file_type,
            "is_jom": False
        }

        messages.append(msg_data)

        if message and "JOM" in message.upper():
            ai_reply = jom_ai_response(message)

            jom_msg = {
                "username": "JOM",
                "message": ai_reply,
                "timestamp": datetime.now().strftime("%H:%M"),
                "file_url": None,
                "file_type": None,
                "is_jom": True
            }

            messages.append(jom_msg)

    return jsonify({"status": "ok"})

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print("Starting FOMISHERS Chat with AI JOM via OpenRouter...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```
