# src/routes/forum_routes.py
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from ..models.question import QuestionCreate
from ..auth import cognito_auth_required # Import the decorator

bp = Blueprint("forum", __name__)

@bp.post("/questions")
@cognito_auth_required # Apply the decorator
def post_question():
    svc = current_app.config["FORUM_SERVICE"]
    try:
        payload = QuestionCreate.model_validate_json(request.data or b"{}")
        out = svc.create_question(payload)
        return out, 201
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

@bp.get("/questions")
def list_questions():
    # Get search parameters with default values
    sort = request.args.get("sort", "new")
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions(limit=limit, sort=sort, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

@bp.get("/questions/me")
@cognito_auth_required
def get_own_questions():
    # Get search parameters with default values
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions_by_user(limit=limit, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

@bp.get("/questions/<qid>")
def get_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    doc = svc.get_question(qid)
    if not doc:
        return {"error": "not_found"}, 404
    return doc, 200

@bp.put("/questions/<qid>")
@cognito_auth_required # Apply the decorator
def edit_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid_json"}), 400

    title = payload.get("title", None)
    body = payload.get("body", None)
    tags = payload.get("tags", None)
    
    if not title and not body and not tags:
        return {"error": "meaningless_request"}, 400

    resp = svc.edit_question(qid=qid, title=title, body=body)
    if not resp:
        return {"error": "question_not_found"}, 404
    if "error" in resp:
        return resp, 400
    return resp, 200

@bp.delete("/questions/<qid>")
@cognito_auth_required
def delete_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    return svc.delete_question(qid=qid)

@bp.post("/questions/<qid>/like")
@cognito_auth_required
def like_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    if svc.like_question(qid):
        return "", 204
    else:
        return {"error": "question_not_found"}, 404

@bp.delete("/questions/<qid>/like")
@cognito_auth_required
def unlike_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    if svc.unlike_question(qid):
        return "", 204
    else:
        return {"error": "question_not_found"}, 404

@bp.get("/questions/<qid>/like")
def get_like_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    liked = svc.get_like_question(qid)
    return {"liked": liked}, 200

@bp.post("/questions/<qid>")
@cognito_auth_required
def post_answer(qid):
    svc = current_app.config["FORUM_SERVICE"]
    return svc.post_answer(qid)