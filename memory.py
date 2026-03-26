import json
import os

FILE = "memory.json"

def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_message(user, message, reply):
    data = load()

    if user not in data:
        data[user] = []

    data[user].append({
        "message": message,
        "reply": reply
    })

    save(data)

def get_memory_summary(user):
    data = load()

    if user not in data:
        return "No stored memories yet."

    important = [
        m["message"] for m in data[user]
        if "like" in m["message"].lower() or "my name" in m["message"].lower()
    ]

    if important:
        return "I remember: " + ", ".join(important[:3])

    return "I remember our chats, but nothing important yet."
