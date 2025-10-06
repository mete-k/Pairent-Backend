# src/routes/bibi_route.py
from random import random
from flask import Blueprint, request, jsonify
import boto3
import os

bp = Blueprint("bibi", __name__)

# Initialize Bedrock client
client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Your existing agent info
AGENT_ID = "MDX1YASPJE"
AGENT_ALIAS_ID = "GEYSFL3PRM"

@bp.route("/bibi", methods=["POST"])
def ask_bibi():
    try:
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("sessionId", "session-001")

        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message,
        )

        full_response = ""
        for event in response["completion"]:
            if "chunk" in event:
                text_piece = event["chunk"]["bytes"].decode("utf-8")
                full_response += text_piece

        return jsonify({"reply": full_response.strip()})

    except Exception as e:
        print("Error invoking Bibi:", e)
        return jsonify({"error": str(e)}), 500

@bp.route("/bibi/daily-tip", methods=["GET"])
def get_daily_tip():
    tips = [
        "Take a few minutes today just for yourself — a calm parent helps a calm child.",
        "Children learn more from what you do than what you say.",
        "Consistency helps kids feel safe — keep routines steady where possible.",
        "Praise effort, not just results — it builds resilience.",
        "Don’t forget: no parent is perfect, but every day is a chance to connect.",
    ]
    return jsonify({"text": random.choice(tips)})

