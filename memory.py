import json
import os

DB = "memory.json"

def load():
    if not os.path.exists(DB):
        return {}
    with open(DB, "r") as f:
        return json.load(f)

def save(data):
    with open(DB, "w") as f:
        json.dump(data, f)

def add_message(user, msg, reply):
    data = load()

    if user not in data:
        data[user] = []

    data[user].append({
        "message": msg,
        "reply": reply
    })

    save(data)
