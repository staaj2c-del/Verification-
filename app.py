from flask import Flask, redirect, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Environment Variables (Set these in Render)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

DATA_FILE = "ip_logs.json"

# Create JSON file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def save_ip(user_id, ip):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data[str(user_id)] = {
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return "Verification system online."

@app.route("/verify")
def verify():
    return redirect(
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")

    token_url = "https://discord.com/api/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(token_url, data=data, headers=headers)
    token_json = token_response.json()

    access_token = token_json.get("access_token")

    if not access_token:
        return "OAuth failed."

    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user_data = user_response.json()
    user_id = user_data.get("id")

    if not user_id:
        return "Failed to fetch user."

    # Get real IP (works behind proxy like Render)
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    save_ip(user_id, user_ip)

    return "Verification complete. You can return to Discord."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
