from flask import Flask, request, jsonify
import requests
import os
from personality import build_personality
from memory import add_message, load

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

# 🧠 Memory recall
def recall_memory(user):
    data = load()
    if user in data:
        last = data[user][-3:]
        return "Here is what I remember:\n" + "\n".join([f"You said: {x['message']}" for x in last])
    return "No memory found."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    user = data.get("user", "User")
    message = data.get("message", "")
    is_admin = data.get("admin", False)
    mode = data.get("mode", "PH03NIX")

    # 🧠 Memory command
    if "remember" in message.lower():
        add_message(user, message, "Stored.")
        return jsonify({"reply": "Noted. I will remember that."})

    if "recall" in message.lower():
        return jsonify({"reply": recall_memory(user)})

    personality = build_personality(user, is_admin, mode)

    prompt = f"""
{personality}

User: {message}
AI:
"""

    reply = query_model(prompt)

    add_message(user, message, reply)

    return jsonify({"reply": reply})


@app.route("/")
def home():
    return "PH03NIX Brain Running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
