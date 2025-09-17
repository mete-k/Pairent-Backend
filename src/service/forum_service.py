# src/services/forum_service.py
import uuid
from flask import g
from datetime import datetime, timezone
from ..db import ensure_table
from ..repo.question_repo import QuestionRepo
from ..models.question import QuestionCreate, Question

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
            answer_count=0
        )
        QuestionRepo.create(q)
        return {"qid": q.qid}

    def get_question(self, qid: str, content: str) -> dict[str, object] | None:
        q = QuestionRepo.get_question(qid)
        return None if q is None else q.model_dump()

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

    def list_questions(self, limit: int, sort: str, last_key: dict[str, str] | None) -> dict[str, object]:
        if sort in ['popular', 'new']:
            res = QuestionRepo.list_questions(limit=limit, sort=sort, last_key=last_key)
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
    def list_questions_by_user(self, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
        res = QuestionRepo.list_questions_by_user(user_id=g.user_sub, limit=limit, last_key=last_key)
        cursor = res.get("LastEvaluatedKey")
        return {
            "items": res["Items"],
            "pageInfo": {
                "hasNextPage": False if cursor == None else True,
                "endCursor": cursor
            }
        }

    # def list_questions_with_tag

def _authorized(qid: str) -> int:
    q = QuestionRepo.get_question(qid)
    if not q:
        return -1
    return int(g.user_sub == q.author_id)