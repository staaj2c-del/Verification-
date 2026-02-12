from flask import Flask, render_template, request
import os, json, requests
from datetime import datetime
from urllib.parse import urlencode

app = Flask(__name__)
DATA_FILE = "../data/verified.json"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def save_verification(discord_id, ip):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    data[str(discord_id)] = {"ip": ip, "claimed": False, "timestamp": datetime.utcnow().isoformat()}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return "<h2>Verification System Online</h2>"

@app.route("/verify")
def verify():
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "Missing Discord ID", 400

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
        "state": discord_id
    }
    oauth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    return render_template("verify.html", oauth_url=oauth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    discord_id = request.args.get("state")
    if not code or not discord_id:
        return "Missing parameters", 400
    try:
        token_url = "https://discord.com/api/oauth2/token"
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "scope": "identify"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_res = requests.post(token_url, data=data, headers=headers).json()
        access_token = token_res.get("access_token")
        if not access_token:
            return "OAuth failed", 400

        user_res = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        verified_id = user_res.get("id")
        if verified_id != discord_id:
            return "Discord ID mismatch!", 400

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        save_verification(discord_id, ip)

        return "<h2>✅ Verification Complete! You can close this page.</h2>"
    except Exception as e:
        print("Callback error:", e)
        return "Internal server error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
