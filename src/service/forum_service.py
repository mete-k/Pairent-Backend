# src/services/forum_service.py
import uuid
from typing import Optional, Dict, Any
from ..repo.question_repo import QuestionRepo
from ..models.question import QuestionCreate, Question, QuestionPublic

class ForumService:
    def __init__(self):
        self.questions = QuestionRepo()

    def create_question(self, author_id: str, payload: QuestionCreate) -> Dict[str, Any]:
        q = Question(
            qid=str(uuid.uuid4()),
            title=payload.title.strip(),
            body=payload.body.strip(),
            author_id=author_id,
            tags=payload.tags,
        )
        self.questions.create(q)
        return {"qid": q.qid}

    def get_question(self, qid: str) -> Optional[Dict[str, Any]]:
        q = self.questions.get(qid)
        return None if q is None else QuestionPublic.from_domain(q).model_dump()

    def edit_question(self, qid: str, title: str = None, body: str = None) -> Dict[str, Any]:
        q = self.questions.edit(qid=qid, title=title, body=body)
        return None if q is None else QuestionPublic.from_domain(q).model_dump()

    def list_questions(self, limit: int = 20, cursor: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        items, last_key = self.questions.list_recent(limit=limit, last_key=cursor)
        return {
            "items": [QuestionPublic.from_domain(q).model_dump() for q in items],
            "nextCursor": last_key
        }
