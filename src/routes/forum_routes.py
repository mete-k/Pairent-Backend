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
            tags: [String], // list of strings
            age: Number
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    try:
        payload = QuestionCreate.model_validate_json(request.data or b"{}")
        out = svc.create_question(payload)
        return out, 201
    except ValidationError as e:
        print(jsonify({"error": "validation", "details": e.errors()}))
        return jsonify({"error": "validation", "details": e.errors()}), 400

# -- Listing questions --
# List questions with optional query parameters
@bp.get("/questions")
def list_questions():
    '''
    Expected query parameters (optional):
        sort: "new" | "popular"                 // default "new"
        direction: "ascending" | "descending"   // default "descending"
        limit: Number                           // number of questions requested with default 10
        after: json                             // provided by backend at last query as ExclusiveStartKey
    '''
    # Get search parameters with default values
    sort = request.args.get("sort", "new")
    dir = request.args.get("direction", "descending")
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions(direction = dir, limit=limit, sort=sort, last_key=last_key)

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
        direction: "ascending" | "descending"   // default "descending"
        after: json // Provided by backend at last query as ExclusiveStartKey
    '''
    # Get search parameters with default values
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))
    dir = request.args.get("direction", "descending")

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions_by_user(direction=dir, limit=limit, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

# Get saved questions
@bp.get("/questions/saved")
@cognito_auth_required
def get_saved_questions():
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
    res = svc.list_saved_questions(limit=limit, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

# List questions with specific tag
@bp.get("/questions/tag/<tag>")
def get_questions_with_tag(tag):
    '''
    Expected query parameters (optional):
        limit: Number                           // number of questions requested with default 10
        direction: "ascending" | "descending"   // default "descending"
        after: json                             // provided by backend at last query as ExclusiveStartKey
    '''
    # Get search parameters with default values
    last_key = request.args.get("after")
    limit = int(request.args.get("limit", 10))
    dir = request.args.get("direction", "descending")

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.list_questions_with_tag(tag=tag, direction=dir, limit=limit, last_key=last_key)

    if "error" in res:
        return res, 400
    return res, 200

# Search questions by text
@bp.get("/questions/search")
def search_questions():
    '''
    Expected query parameters:
        q: String                               // search query
    Optional query parameters:
        limit: Number                           // number of questions requested with default 10
        direction: "ascending" | "descending"   // default "descending"
        after: json                             // provided by backend at last query as ExclusiveStartKey
    '''
    # Get search parameters with default values
    query = request.args.get("q", "")
    if not query:
        return {"error": "missing_query_parameter"}, 400

    last_key = request.args.get("after", {})
    limit = int(request.args.get("limit", 10))
    dir = request.args.get("direction", "descending")

    # Hand over to service
    svc = current_app.config["FORUM_SERVICE"]
    res = svc.search_questions(query=query, direction=dir, limit=limit, last_key=last_key)

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
    cont: str = request.args.get("content", "all")
    svc = current_app.config["FORUM_SERVICE"]
    doc = svc.get_question(qid, cont)
    if not doc:
        return {"error": "not_found"}, 404
    return doc, 200

# Edit the question
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

# ---- Like routes ----
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

# ---- Save routes ----
@bp.post("/questions/<qid>/save")
@cognito_auth_required
def save_question(qid):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    if svc.save_question(qid):
        return "", 204
    else:
        return {"error": "question_not_found"}, 404

@bp.delete("/questions/<qid>/save")
@cognito_auth_required
def unsave_question(qid):
    '''
    Expected headers:
        {
            "Authorization": "Bearer {accessToken}"
        }
    '''
    svc = current_app.config["FORUM_SERVICE"]
    if svc.unsave_question(qid):
        return "", 204
    else:
        return {"error": "question_not_found"}, 404

# ---- Reply routes ----
@bp.post("/questions/<qid>/reply")
@cognito_auth_required
def post_reply(qid):
    svc = current_app.config["FORUM_SERVICE"]
    return svc.create_reply(qid)