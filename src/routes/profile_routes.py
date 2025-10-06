# src/routes/profile_routes.py
from flask import Blueprint, request, jsonify, current_app, g
from pydantic import ValidationError
from ..auth import cognito_auth_required
from ..models.profile import ProfileCreate, ProfileUpdate, ChildCreate, ChildUpdate, GrowthCreate, VaccineCreate
from ..service import profile_service as svc

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
    try:
        payload = ProfileCreate.model_validate(payload)
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400
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
    svc = current_app.config["PROFILE_SERVICE"] 
    payload = request.get_json(force=True)
    out = svc.update_profile(payload)
    return jsonify(out), 200

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
    return svc.get_user_profile(g.user_sub, user_id), 200

# ---- Children ----

# Add child
@bp.post("/profile/me/children")
@cognito_auth_required
def add_child():
    svc = current_app.config["PROFILE_SERVICE"]
    try:
        payload = request.get_json(force=True)
        payload = ChildCreate.model_validate(payload)
        return svc.add_child(payload), 201
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

# Update child
@bp.put("/profile/me/children/<child_id>")
@cognito_auth_required
def update_child(child_id):
    from flask import g, current_app, request
    from ..models.profile import ChildUpdate
    from ..service.profile_service import ProfileService

    payload = request.get_json()
    current_app.logger.info(f"[ROUTE] PUT /profile/me/children/{child_id} payload: {payload}")

    update_model = ChildUpdate.model_validate(payload)
    data = update_model.model_dump(exclude_none=True)
    current_app.logger.info(f"[ROUTE] Parsed ChildUpdate: {data}")

    svc = ProfileService()
    result = svc.update_child(child_id, update_model)

    return jsonify(result), 200

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

# List children
@bp.get("/profile/me/children")
@cognito_auth_required
def list_children():
    """
    Get all children for the authenticated user.
    Expected headers:
        Authorization: Bearer {accessToken}
    """
    svc = current_app.config["PROFILE_SERVICE"]
    return jsonify(svc.list_children()), 200

# Add growth record
@bp.post("/profile/me/children/<child_id>/growth")
@cognito_auth_required
def add_growth(child_id):
    svc = current_app.config["PROFILE_SERVICE"]
    try:
        payload = request.get_json(force=True)
        growth_data = GrowthCreate.model_validate(payload)
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

    return svc.add_growth(child_id, growth_data), 201

# Add vaccine record
@bp.post("/profile/me/children/<child_id>/vaccine")
@cognito_auth_required
def add_vaccine(child_id):
    svc = current_app.config["PROFILE_SERVICE"]
    try:
        payload = request.get_json(force=True)
        vaccine_data = VaccineCreate.model_validate(payload)
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

    return svc.add_vaccine(child_id, vaccine_data), 201

# ---- List growth records ----
@bp.get("/profile/me/children/<child_id>/growth")
@cognito_auth_required
def list_growth(child_id):
    """
    List all growth records for the given child.
    """
    svc = current_app.config["PROFILE_SERVICE"]
    return jsonify(svc.list_growth(child_id)), 200

# ---- List vaccine records ----
@bp.get("/profile/me/children/<child_id>/vaccine")
@cognito_auth_required
def list_vaccine(child_id):
    """
    List all vaccine records for the given child.
    """
    svc = current_app.config["PROFILE_SERVICE"]
    return jsonify(svc.list_vaccine(child_id)), 200


# ---- Milestones ----
@bp.get("/milestones/<child_id>")
@cognito_auth_required
def list_milestones(child_id):
    """
    Get milestone progress for the given child.
    """
    svc = current_app.config["PROFILE_SERVICE"]
    return jsonify(svc.list_milestones(child_id)), 200

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
