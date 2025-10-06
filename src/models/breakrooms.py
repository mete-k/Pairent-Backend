# src/routes/breakrooms.py
from flask import Blueprint, jsonify, request
import requests
import os

bp = Blueprint("breakrooms", __name__)
DAILY_API_KEY = os.getenv("DAILY_API_KEY")
DAILY_API_URL = "https://api.daily.co/v1"

# --- Create a new Daily room ---
@bp.route("/breakrooms", methods=["POST"])
def create_breakroom():
    try:
        payload = {
            "name": request.json.get("name"),
            "privacy": "private",       # or "public"
            "properties": {
                "enable_chat": True,
                "start_audio_off": False,
                "start_video_off": True,
                "exp": int((__import__('time').time()) + 3600)  # expires in 1h
            }
        }

        headers = {"Authorization": f"Bearer {DAILY_API_KEY}"}
        resp = requests.post(f"{DAILY_API_URL}/rooms", json=payload, headers=headers)
        data = resp.json()

        if resp.status_code != 200:
            return jsonify({"error": data}), resp.status_code

        return jsonify({"url": data["url"], "name": data["name"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- List existing rooms ---
@bp.route("/breakrooms", methods=["GET"])
def list_breakrooms():
    headers = {"Authorization": f"Bearer {DAILY_API_KEY}"}
    resp = requests.get(f"{DAILY_API_URL}/rooms", headers=headers)
    return jsonify(resp.json())
