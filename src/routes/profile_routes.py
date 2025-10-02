# src/routes/profile_routes.py
from flask import Blueprint, request, jsonify, current_app, g
from pydantic import ValidationError
from ..auth import cognito_auth_required

bp = Blueprint("profile", __name__)

# ---- Profile ----
# Create profile (called after signup)
@bp.post("/profile")
def create_profile():
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            user_id: String,
            name: String,
            dob: String
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    payload = request.get_json(force=True)
    out = svc.create_profile(payload=payload)
    return out, 201

# Get own profile
@bp.get("/profile/me")
@cognito_auth_required
def get_my_profile():
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    return svc.get_my_profile(), 200


# Update own profile (children, privacy, etc.)
@bp.put("/profile/me")
@cognito_auth_required
def update_my_profile():
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            children: [ ... ],
            profile_privacy: { ... }
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    try:
        payload = request.get_json(force=True)
        out = svc.update_my_profile(payload)
        return out, 200
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400


# Get another user's profile (privacy filtered)
@bp.get("/profile/<user_id>")
@cognito_auth_required
def get_user_profile(user_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    return svc.get_user_profile(user_id), 200


# ---- Children ----

# Add child
@bp.post("/profile/me/children")
@cognito_auth_required
def add_child():
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            name: String,
            dob: String
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    payload = request.get_json(force=True)
    return svc.add_child(payload), 201


# Update child
@bp.put("/profile/me/children/<child_id>")
@cognito_auth_required
def update_child(child_id):
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    payload = request.get_json(force=True)
    return svc.update_child(child_id, payload), 200


# Delete child
@bp.delete("/profile/me/children/<child_id>")
@cognito_auth_required
def delete_child(child_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    svc.delete_child(child_id)
    return "", 204


# Add growth record
@bp.post("/profile/me/children/<child_id>/growth")
@cognito_auth_required
def add_growth(child_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            date: String,
            height: Number,
            weight: Number
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    payload = request.get_json(force=True)
    return svc.add_growth(child_id, payload), 201


# Add vaccine record
@bp.post("/profile/me/children/<child_id>/vaccine")
@cognito_auth_required
def add_vaccine(child_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            name: String,
            date: String,
            status: "done" | "pending" | "skipped"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    payload = request.get_json(force=True)
    return svc.add_vaccine(child_id, payload), 201


# ---- Friends ----

# Send friend request
@bp.post("/friends/request/<user_id>")
@cognito_auth_required
def send_friend_request(user_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    return svc.send_friend_request(user_id), 201


# Accept friend request
@bp.post("/friends/accept/<user_id>")
@cognito_auth_required
def accept_friend_request(user_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    return svc.accept_friend_request(user_id), 200


# List pending friend requests
@bp.get("/friends/requests")
@cognito_auth_required
def list_friend_requests():
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    return svc.list_friend_requests(), 200


# Remove a friend
@bp.delete("/friends/<user_id>")
@cognito_auth_required
def remove_friend(user_id):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["PROFILE_SERVICE"]
    svc.remove_friend(user_id)
    return "", 204
