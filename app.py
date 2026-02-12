from flask import Flask, request, render_template, jsonify
import requests, os

app = Flask(__name__)

BOT_ENDPOINT = os.getenv("BOT_ENDPOINT")  # e.g., http://BOT_URL:5001/verify
BOT_API_KEY = os.getenv("BOT_API_KEY")    # same as in bot

@app.route("/")
def home():
    return "<h2>Verification System Online</h2>"

@app.route("/verify")
def verify():
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "Missing Discord ID", 400
    return render_template("verify.html", discord_id=discord_id)

@app.route("/complete", methods=["POST"])
def complete_verification():
    data = request.json
    discord_id = data.get("discord_id")
    ip = request.remote_addr
    if not discord_id:
        return jsonify({"status":"error","message":"Missing Discord ID"}), 400

    # Send to bot API
    res = requests.post(BOT_ENDPOINT, json={"discord_id": discord_id, "ip": ip, "key": BOT_API_KEY})
    if res.status_code == 200:
        return jsonify({"status":"success","message":res.json().get("message")})
    return jsonify({"status":"error","message":"Bot failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
