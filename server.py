from flask import Flask, request, jsonify, render_template
import requests
import os
from personality import build_personality
from memory import add_message, get_memory_summary

app = Flask(__name__)

MODEL_API = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HEADERS = {"Content-Type": "application/json"}

def query_model(prompt):
    try:
        r = requests.post(MODEL_API, headers=HEADERS, json={"inputs": prompt}, timeout=60)
        data = r.json()
        if isinstance(data, list):
            return data[0]["generated_text"]
        return "Processing..."
    except:
        return "Systems initializing..."

# 🧠 MAIN PAGE
@app.route("/")
def home():
    return render_template("chat.html")

# 🧠 CHAT API
@app.route("/send", methods=["POST"])
def send():
    data = request.json

    user = data.get("username", "User")
    message = data.get("message", "")

    # MEMORY COMMANDS
    if "remember" in message.lower():
        add_message(user, message, "Stored")
        return jsonify({"reply": "Noted. I will remember that."})

    if "recall" in message.lower():
        return jsonify({"reply": get_memory_summary(user)})

    personality = build_personality(user)

    prompt = f"""
{personality}

User: {message}
AI:
"""

    reply = query_model(prompt)

    add_message(user, message, reply)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
