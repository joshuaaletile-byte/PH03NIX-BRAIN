from flask import Flask, request, jsonify, render_template
import requests
import os
import threading
import time
from memory import add_message, get_memory_summary

app = Flask(__name__)

# 🔑 KEYS
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🧠 REAL AI FUNCTION
def ai_reply(user, message):

    # MEMORY COMMANDS
    if "remember" in message.lower():
        add_message(user, message, "stored")
        return "Noted. I will remember that."

    if "recall" in message.lower():
        return get_memory_summary(user)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are PH03NIX, a smart AI like JARVIS. Be intelligent, clear, and slightly futuristic."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            timeout=30
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI error:", e)
        return "Systems are stabilizing... try again."

# 🌐 WEB
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    user = data.get("username", "User")
    message = data.get("message", "")

    reply = ai_reply(user, message)

    add_message(user, message, reply)

    return jsonify({"reply": reply})

# 🤖 TELEGRAM BOT
def telegram_bot():
    offset = None
    print("Telegram bot running...")

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

                reply = ai_reply(user, msg)

                requests.post(f"{BASE}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": reply + "\n\n— PH03NIX —"
                })

            time.sleep(1)

        except Exception as e:
            print("Bot error:", e)
            time.sleep(5)

# START BOT
def start_bot():
    if BOT_TOKEN:
        thread = threading.Thread(target=telegram_bot)
        thread.daemon = True
        thread.start()

start_bot()

# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
