from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

BOT_ENDPOINT = os.getenv("BOT_ENDPOINT")  # e.g., http://BOT_IP:5001/verify
BOT_API_KEY = os.getenv("BOT_API_KEY")    # must match bot

@app.route("/")
def home():
    return "<h2>Verification System Online</h2>"

@app.route("/verify")
def verify():
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "Missing Discord ID", 400

    # Grab visitor IP automatically
    user_ip = request.remote_addr

    # Send verification to bot
    try:
        res = requests.post(BOT_ENDPOINT, json={
            "discord_id": discord_id,
            "ip": user_ip,
            "key": BOT_API_KEY
        })
        if res.status_code == 200:
            return f"✅ {res.json().get('message')}"
        else:
            return f"❌ Verification failed: {res.text}", 400
    except Exception as e:
        return f"❌ Error sending to bot: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
