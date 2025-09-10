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
            qid=str(uuid.uuid4()),
            title=payload.title.strip(),
            body=payload.body.strip(),
            author_id=g.user_sub,
            tags=payload.tags,
            age=payload.age,
            created_at=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            likes=0,
            answer_count=0
        )
        QuestionRepo.create(q)
        return {"qid": q.qid}

    def get_question(self, qid: str) -> dict[str, object] | None:
        q = QuestionRepo.get(qid)
        return None if q is None else q.model_dump()

    def edit_question(self, qid: str, title: str = None, body: str = None) -> dict[str, object] | None:
        authorship = _authorized(qid)
        if authorship == -1:
            return None
        elif authorship == 0:
            return {"error": "not_authorized"}
        q = QuestionRepo.edit(qid=qid, title=title, body=body)
        return None if q is None else q.model_dump()
    
    def delete_question(self, qid: str) -> bool:
        authorship = _authorized(qid)
        if authorship == -1:
            return None
        elif authorship == 0:
            return {"error": "not_authorized"}
        return QuestionRepo.delete(qid)

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
    q = QuestionRepo.get(qid)
    if not q:
        return -1
    return int(g.user_sub == q.user_id)