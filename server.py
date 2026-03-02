from flask import Flask, request, jsonify
from personality import build_personality
from memory import add_message
import requests

app = Flask(__name__)

MODEL_ENDPOINT = "http://localhost:11434/api/generate"
# This will be provided by the free AI runtime we install.

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user = data.get("user")
    message = data.get("message")
    is_admin = data.get("admin", False)
    mode = data.get("mode", "PH03NIX")

    system_prompt = build_personality(user, is_admin, mode)

    payload = {
        "model": "tinyllm",
        "prompt": system_prompt + "\nUser: " + message,
        "stream": False
    }

    response = requests.post(MODEL_ENDPOINT, json=payload).json()
    reply = response.get("response", "No reply")

    add_message(user, message, reply)

    return jsonify({"reply": reply})

@app.route("/")
def home():
    return "PH03NIX Brain Running"
