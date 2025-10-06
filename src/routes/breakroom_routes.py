from flask import Blueprint, jsonify, request
import os, requests, time

bp = Blueprint("breakrooms", __name__)
DAILY_API_KEY = os.getenv("DAILY_API_KEY")
DAILY_API_URL = "https://api.daily.co/v1/rooms"

def _headers():
    return {"Authorization": f"Bearer {DAILY_API_KEY}"}

# ---------- List Breakrooms ----------
@bp.route("/breakrooms", methods=["GET"])
def list_breakrooms():
    try:
        resp = requests.get(DAILY_API_URL, headers=_headers())
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Create Breakroom ----------
@bp.route("/breakrooms", methods=["POST"])
def create_breakroom():
    import os, re, time, requests
    from flask import request, jsonify

    try:
        data = request.get_json() or {}
        print("Received data:", data)

        DAILY_API_KEY = os.getenv("DAILY_API_KEY")
        if not DAILY_API_KEY:
            print("DAILY_API_KEY missing or not loaded")
            return jsonify({"error": "Missing API key"}), 500

        raw_name = data.get("name", f"room_{int(time.time())}")
        name = re.sub(r"[^A-Za-z0-9_-]", "-", raw_name)
        description = data.get("description", "")

        payload = {
            "name": name,
            "privacy": "public",
            "properties": {
                "enable_chat": True,
                "start_audio_off": False,
                "start_video_off": True,
                "exp": int(time.time()) + 3600,
            },
        }

        headers = {
            "Authorization": f"Bearer {DAILY_API_KEY}",
            "Content-Type": "application/json",
        }

        print("Payload sent to Daily:", payload)
        resp = requests.post("https://api.daily.co/v1/rooms", json=payload, headers=headers)
        print("Daily response:", resp.status_code, resp.text)

        # Handle Daily errors cleanly
        if resp.status_code != 200:
            return jsonify({"error": resp.json()}), resp.status_code

        room = resp.json()
        return jsonify({
            "id": room["name"],
            "name": room["name"],
            "url": room["url"],
            "description": description,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
