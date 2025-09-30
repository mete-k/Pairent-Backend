from flask import Blueprint, jsonify, g, current_app
from ..auth import cognito_auth_required
from .. import breakroom_service as service

bp = Blueprint("breakrooms", __name__)

@bp.post("/breakrooms")
@cognito_auth_required
def create_breakroom():
    try:
        data = service.create_breakroom(g.user_sub, g.username)
        return jsonify(data), 201
    except Exception as e:
        current_app.logger.error("Failed to create breakroom: %s", str(e))
        return jsonify({"error": "daily_room_creation_failed"}), 502

@bp.post("/breakrooms/<room_id>/tokens")
@cognito_auth_required
def issue_token(room_id):
    try:
        token_data, err = service.issue_token(room_id, g.user_sub, g.username)
        if err == "room_not_found": return jsonify({"error": err}), 404
        if err == "room_not_active": return jsonify({"error": err}), 409
        return jsonify(token_data), 200
    except Exception as e:
        current_app.logger.error("Failed to issue token: %s", str(e))
        return jsonify({"error": "token_issue_failed"}), 502

@bp.delete("/breakrooms/<room_id>")
@cognito_auth_required
def end_breakroom(room_id):
    try:
        err = service.end_breakroom(room_id, g.user_sub, getattr(g, "groups", []))
        if err == "room_not_found": return jsonify({"error": err}), 404
        if err == "forbidden": return jsonify({"error": err}), 403
        return jsonify({"message": "Room ended"}), 200
    except Exception as e:
        current_app.logger.error("Failed to end breakroom: %s", str(e))
        return jsonify({"error": "daily_room_delete_failed"}), 502

@bp.get("/breakrooms/<room_id>")
@cognito_auth_required
def get_breakroom(room_id):
    try:
        data = service.get_breakroom(room_id)
        if not data:
            return jsonify({"error": "room_not_found"}), 404
        return jsonify(data), 200
    except Exception as e:
        current_app.logger.error("Failed to fetch breakroom: %s", str(e))
        return jsonify({"error": "room_fetch_failed"}), 502

@bp.get("/breakrooms")
@cognito_auth_required
def list_breakrooms():
    try:
        rooms = service.list_breakrooms()
        return jsonify(rooms), 200
    except Exception as e:
        current_app.logger.error("Failed to list breakrooms: %s", str(e))
        return jsonify({"error": "room_list_failed"}), 502
