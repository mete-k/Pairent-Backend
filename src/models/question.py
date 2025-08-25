# src/models/question.py
from pydantic import BaseModel, Field
from typing import List, Optional
import time

# Incoming payload
class QuestionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str = ""
    tags: List[str] = []

# Domain model (what your service works with)
class Question(BaseModel):
    qid: str
    title: str
    body: str = ""
    author_id: str
    tags: List[str] = []
    created_at: int = Field(default_factory=lambda: int(time.time()))
    score: int = 0
    answer_count: int = 0

# Outbound (public) shape for API responses
class QuestionPublic(BaseModel):
    qid: str
    title: str
    body: str
    authorId: str
    tags: List[str]
    createdAt: int
    score: int
    answerCount: int

    @classmethod
    def from_domain(cls, q: Question) -> "QuestionPublic":
        return cls(
            qid=q.qid,
            title=q.title,
            body=q.body,
            authorId=q.author_id,
            tags=q.tags,
            createdAt=q.created_at,
            score=q.score,
            answerCount=q.answer_count,
        )

# -------- DynamoDB mappers (single-table PK/SK) --------
def to_item(q: Question) -> dict:
    return {
        "PK": f"QUESTION#{q.qid}",
        "SK": "META",
        "qid": q.qid,
        "title": q.title,
        "body": q.body,
        "authorId": q.author_id,
        "tags": q.tags,
        "createdAt": q.created_at,
        "score": q.score,
        "answerCount": q.answer_count,
    }

def from_item(item: Optional[dict]) -> Optional[Question]:
    if not item:
        return None
    return Question(
        qid=item["qid"],
        title=item["title"],
        body=item.get("body", ""),
        author_id=item["authorId"],
        tags=item.get("tags", []),
        created_at=item["createdAt"],
        score=item.get("score", 0),
        answer_count=item.get("answerCount", 0),
    )
