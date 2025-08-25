# src/routes/forum_routes.py
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from ..models.question import QuestionCreate

bp = Blueprint("forum", __name__)

@bp.post("/questions")
def post_question():
    svc = current_app.config["FORUM_SERVICE"]
    try:
        payload = QuestionCreate.model_validate_json(request.data or b"{}")
        author_id = request.headers.get("X-User-Id", "mock-user")
        out = svc.create_question(author_id, payload)
        return out, 201
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

@bp.get("/questions/<qid>")
def get_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    doc = svc.get_question(qid)
    if not doc:
        return {"error": "not_found"}, 404
    return doc, 200

@bp.put("/questions/<qid>")
def edit_question(qid):
    svc = current_app.config["FORUM_SERVICE"]
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "invalid_json"}), 400

    title = payload.get("title", None)
    body = payload.get("body", None)
    resp = svc.edit_question(qid=qid, title=title, body=body)
    if not resp:
        return {"error": "something_went_wrong"}, 400
    return resp, 200

@bp.get("/questions")
def list_questions():
    svc = current_app.config["FORUM_SERVICE"]
    limit = int(request.args.get("limit", 20))
    res = svc.list_questions(limit=limit, cursor=None)  # add cursor parsing later
    return res, 200
