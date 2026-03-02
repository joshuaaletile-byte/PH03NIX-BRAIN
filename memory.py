import json
import os

DB = "memory.json"

def load_memory():
    if not os.path.exists(DB):
        return {}
    with open(DB, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(DB, "w") as f:
        json.dump(data, f)

def add_message(user, message, reply):
    data = load_memory()
    if user not in data:
        data[user] = []
    data[user].append({"msg": message, "reply": reply})
    save_memory(data)
