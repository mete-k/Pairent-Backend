from flask import Blueprint, request, jsonify, current_app

bp = Blueprint("forum", __name__)

@bp.post("/questions")
def post_question():
    svc = current_app.config["FORUM_SVC"]
    j = request.get_json(force=True) or {}
    try:
        out = svc.create_question(
            author_id=request.headers.get("X-User-Id", "mock-user"),
            title=j.get("title", ""),
            body=j.get("body", ""),
            tags=j.get("tags", []),
        )
        return out, 201
    except ValueError as e:
        return jsonify({"error": "bad_request", "message": str(e)}), 400
@bp.get("/questions/<qid>")
def get_question(qid: str):
    svc = current_app.config["FORUM_SVC"]
    try:
        out = svc.get_question(qid)
        return out, 200
    except ValueError as e:
        return jsonify({"error": "bad_request", "message": str(e)}), 400
