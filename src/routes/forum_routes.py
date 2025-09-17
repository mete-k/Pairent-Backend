# src/routes/forum_routes.py
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from ..models.question import QuestionCreate
from ..auth import cognito_auth_required # Import the decorator

bp = Blueprint("forum", __name__)

# ---- Questions ----
# Post a question
@bp.post("/questions")
@cognito_auth_required
def post_question():
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    Expected body:
        {
            title: String,
            body: String,
            tags: [String],
            age: Number
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    try:
        payload = QuestionCreate.model_validate_json(request.data or b"{}")
        out = svc.create_question(payload)
        return out, 201
    except ValidationError as e:
        return jsonify({"error": "validation", "details": e.errors()}), 400

# List questions with optional query parameters
@bp.get("/questions")
def list_questions():
    '''
    Expected query parameters (optional):
        sort: "new" | "popular"
        limit: Number   // number of questions requested
        after: json     // provided by backend at last query as ExclusiveStartKey
    '''
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

# Get questions posted by user
@bp.get("/questions/me")
@cognito_auth_required
def get_own_questions():
    '''
    Expected query parameters (optional):
        limit: Number
        after: json // Provided by backend at last query as ExclusiveStartKey
    '''
    # Get search parameters with default values
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions_by_user(limit=limit, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

# Get a specific question and related answers etc.
@bp.get("/questions/<qid>")
def get_question(qid):
    '''
    Expected query parameters (optional):
        content: "all" | "question"
    '''
    # Not implemented yet
    cont: str = request.args.get("content", "all")
    svc = current_app.config["FORUM_SERVICE"]
    doc = svc.get_question(qid, cont)
    if not doc:
        return {"error": "not_found"}, 404
    return doc, 200

@bp.put("/questions/<qid>")
@cognito_auth_required # Apply the decorator
def edit_question(qid):
    '''
    Expected headers:
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer {accessToken}"
        }
    Expected body (each attribute optional):
        {
            title: String,
            body: String,
            tags: [String]
        }
    '''
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
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    return svc.delete_question(qid=qid)

# ---- Like related routes ----
@bp.post("/questions/<qid>/like")
@cognito_auth_required
def like_question(qid):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    if svc.like_question(qid):
        return "", 204
    else:
        return {"error": "question_not_found"}, 404

@bp.delete("/questions/<qid>/like")
@cognito_auth_required
def unlike_question(qid):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
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
    '''
    TODO: implement answers
    '''
    svc = current_app.config["FORUM_SERVICE"]
    return svc.post_answer(qid)