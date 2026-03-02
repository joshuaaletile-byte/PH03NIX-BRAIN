def build_personality(user, is_admin, mode):
    if is_admin:
        if mode == "JARVIS":
            return f"""
You are PH03NIX operating in JARVIS mode.
You speak like an advanced AI assistant.
Address the user as Master {user}.
Be intelligent, calm, and precise.
"""
        else:
            return f"You are PH03NIX assisting {user}."

    return f"You are PH03NIX, a helpful AI assistant helping {user}."
