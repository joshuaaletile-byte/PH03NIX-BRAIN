from flask import Flask, request, jsonify, render_template
import requests
import os
import threading
import time
from personality import build_personality
from memory import add_message, get_memory_summary

app = Flask(__name__)

# 🔑 CONFIG
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

MODEL_API = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# 🧠 AI MODEL
def query_model(prompt):
    try:
        r = requests.post(MODEL_API, json={"inputs": prompt}, timeout=60)
        data = r.json()
        if isinstance(data, list):
            return data[0]["generated_text"]
        return "Processing..."
    except:
        return "Systems stabilizing..."

# 🌐 WEB ROUTES
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send", methods=["POST"])
def send():
    data = request.json

    user = data.get("username", "User")
    message = data.get("message", "")

    # MEMORY
    if "remember" in message.lower():
        add_message(user, message, "Stored")
        return jsonify({"reply": "Noted. Memory stored."})

    if "recall" in message.lower():
        return jsonify({"reply": get_memory_summary(user)})

    personality = build_personality(user)

    prompt = f"{personality}\nUser: {message}\nAI:"
    reply = query_model(prompt)

    add_message(user, message, reply)

    return jsonify({"reply": reply})

# 🤖 TELEGRAM BOT LOOP
def telegram_bot():
    offset = None
    print("Telegram bot started")

    while True:
        try:
            res = requests.get(
                f"{BASE}/getUpdates",
                params={"timeout": 100, "offset": offset}
            ).json()

            for item in res["result"]:
                offset = item["update_id"] + 1

                if "message" not in item:
                    continue

                msg = item["message"].get("text", "")
                chat_id = item["message"]["chat"]["id"]
                user = item["message"]["from"].get("first_name", "User")

                r = requests.post("http://127.0.0.1:5000/send", json={
                    "username": user,
                    "message": msg
                }).json()

                reply = r.get("reply", "Thinking...")

                requests.post(f"{BASE}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": reply + "\n\n— PH03NIX —"
                })

            time.sleep(1)

        except Exception as e:
            print("Bot error:", e)
            time.sleep(5)

# 🚀 START BOT THREAD
def start_bot():
    if BOT_TOKEN:
        thread = threading.Thread(target=telegram_bot)
        thread.daemon = True
        thread.start()

start_bot()

# ▶️ RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
