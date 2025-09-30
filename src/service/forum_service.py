# src/services/forum_service.py
import uuid
from flask import g
from datetime import datetime, timezone
from ..db import ensure_table, forum_table as table
from ..repo import question_repo as QuestionRepo
from ..repo import reply_repo as ReplyRepo
from ..models.question import QuestionCreate, Question
from ..models.reply import ReplyCreate, Reply
from ..models.forum import to_save

class ForumService:
    def __init__(self) -> None:
        ensure_table()
    def create_question(self, payload: QuestionCreate) -> dict[str, object]:
        q = Question(
            qid=uuid.uuid4().hex,
            title=payload.title.strip(),
            body=payload.body.strip(),
            author_id=g.user_sub,
            tags=payload.tags,
            age=payload.age,
            created_at=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            likes=0,
            reply_count=0
        )
        QuestionRepo.create(q)
        return q.model_dump()

    def get_question(self, qid: str, content: str) -> dict[str, object] | None:
        if content == "question":
            q = QuestionRepo.get_question(qid)
            return None if q is None else q.model_dump()
        elif content == "all":
            forum = QuestionRepo.get_forum(qid, all=False)
            return forum
        else:
            return {"error": "invalid_query_parameter"}

    def edit_question(self, qid: str, title: str = "", body: str = "") -> dict[str, object] | None:
        authorship = _authorized(qid)
        if authorship == -1:
            return None
        elif authorship == 0:
            return {"error": "not_authorized"}
        q = QuestionRepo.edit(qid=qid, title=title, body=body)
        return None if q is None else q.model_dump()
    
    def delete_question(self, qid: str) -> tuple[dict[str, str] | str, int]:
        authorship = _authorized(qid)
        if authorship == 0:
            return {"error": "not_authorized"}, 403
        QuestionRepo.delete(qid)
        return "", 204

    def like_question(self, qid: str) -> bool:
        return QuestionRepo.like(qid)
    def unlike_question(self, qid: str) -> bool:
        return QuestionRepo.unlike(qid)
    def get_like_question(self, qid: str) -> bool:
        return QuestionRepo.get_like(qid)
    
    def save_question(self, qid: str) -> bool:
        return QuestionRepo.save_question(qid=qid)
    def unsave_question(self, qid: str) -> bool:
        return QuestionRepo.unsave_question(qid=qid)

    def list_questions(self, direction: str, limit: int, sort: str, last_key: dict[str, str] | None) -> dict[str, object]:
        if sort in ['popular', 'new']:
            match direction:
                case 'descending' | 'desc':
                    dir = False
                case 'ascending' | 'asc':
                    dir = True
                case _:
                    return {"error": "invalid_direction_parameter"}
            res = QuestionRepo.list_questions(direction=dir, limit=limit, sort=sort, last_key=last_key)
        else:
            return {"error": "invalid_sort_parameter"}
        cursor = res.get("LastEvaluatedKey")
        return {
            "items": res["Items"],
            "pageInfo": {
                "hasNextPage": False if cursor == None else True,
                "endCursor": cursor
            }
        }
    def list_questions_by_user(self, direction: str, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
        dir = _resolve_direction(direction)
        if dir is None:
            return {"error": "invalid_direction_parameter"}
        res = QuestionRepo.list_questions_by_user(direction=dir, limit=limit, last_key=last_key)
        cursor = res.get("LastEvaluatedKey")
        return {
            "items": res["Items"],
            "pageInfo": {
                "hasNextPage": False if cursor == None else True,
                "endCursor": cursor
            }
        }

    def list_saved_questions(self, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
        limit = max(1, min(limit, 20))  # enforce 1 <= limit <= 20
        saves_res = QuestionRepo.get_saves(limit=limit, last_key=last_key)
        cursor = saves_res.get("LastEvaluatedKey")
        saves = saves_res.get("Items", [])
        save_objs = [to_save(s) for s in saves]
        qids = [s.qid for s in save_objs]
        questions = QuestionRepo.get_questions_by_qids(qids)
        if len(questions) != limit:
            for i, qid in enumerate(qids):
                if not any(q["qid"] == qid for q in questions):
                    table.delete_item(Key=save_objs[i].key())
        return {
            "items": questions,
            "pageInfo": {
                "hasNextPage": False if cursor == None else True,
                "endCursor": cursor
            }
        }
    
    # Search questions by the content of their titles and bodies
    def search_questions(self, query: str, direction: str, limit: int, last_key: dict[str, str]) -> dict[str, object]:
        dir = _resolve_direction(direction)
        if dir is None:
            return {"error": "invalid_direction_parameter"}
        return QuestionRepo.search_questions(query=query, direction=dir, limit=limit, last_key=last_key)

    def list_questions_with_tag(self, tag: str, direction: bool, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
        res = QuestionRepo.list_questions_with_tag(tag=tag, direction=direction, limit=limit, last_key=last_key)
        cursor = res.get("LastEvaluatedKey")
        return {
            "items": res["Items"],
            "pageInfo": {
                "hasNextPage": False if cursor == None else True,
                "endCursor": cursor
            }
        }

    # ---- Replies ----
    def create_reply(self, qid: str, payload: dict) -> dict[str, object] | tuple[dict[str, object], int]:
        try:
            data = ReplyCreate(**payload)
        except Exception as e:
            return {"error": "validation", "details": str(e)}, 400

        rid = uuid.uuid4().hex
        reply = Reply(
            qid=qid,
            rid=rid,
            parent_id=data.parent_id,
            user_id=g.user_sub,
            body=data.body.strip(),
            created_at=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            likes=0,
            reply_count=0
        )
        ReplyRepo.create(reply)
        return {"rid": rid}

    def get_reply(self, qid: str, rid: str) -> dict[str, object] | None:
        reply = ReplyRepo.get_reply(qid, rid)
        return None if reply is None else reply.model_dump()
    
    def edit_reply(self, qid: str, rid: str, payload: dict) -> dict[str, object] | tuple[dict[str, object], int]:
        reply = ReplyRepo.get_reply(qid, rid)
        if not reply:
            return {"error": "not_found"}, 404
        if reply.user_id != g.user_sub:
            return {"error": "not_authorized"}, 403
        body = payload.get("body", "")
        if not body:
            return {"error": "meaningless_request"}, 400
        ReplyRepo.edit(qid, rid, body)
        updated = ReplyRepo.get_reply(qid, rid)
        return updated.model_dump() if updated else {"error": "not_found"}, 200

    def delete_reply(self, qid: str, rid: str) -> tuple[dict[str, object], int] | int:
        reply = ReplyRepo.get_reply(qid, rid)
        if not reply:
            return {"error": "not_found"}, 404
        if reply.user_id != g.user_sub:
            return {"error": "not_authorized"}, 403
        ok = ReplyRepo.delete(qid, rid)
        if ok:
            return 204
        else:
            return {"error": "delete_failed"}, 500
    
    def like_reply(self, qid: str, rid: str) -> bool:
        return ReplyRepo.like(qid, rid)
    def unlike_reply(self, qid: str, rid: str) -> bool:
        return ReplyRepo.unlike(qid, rid)


def _authorized(qid: str) -> int:
    q = QuestionRepo.get_question(qid)
    if not q:
        return -1
    return int(g.user_sub == q.author_id)

def _resolve_direction(direction: str) -> bool | None:
    match direction:
        case 'descending' | 'desc':
            return False
        case 'ascending' | 'asc':
            return True
        case _:
            return None
        
# def _validate_last_key(last_key: dict[str, str] | None) -> dict[str, str] | None:
#     if not last_key:
#         return None
#     if "PK" in last_key and "SK" in last_key:
#         return last_key
#     return None