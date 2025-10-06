from pydantic import BaseModel, Field
from typing import Optional, List


# ---- Incoming payload ----
class QuestionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str
    tags: List[str] = []
    age: int


# ---- Primary model ----
class Question(BaseModel):
    qid: str
    title: str
    body: str
    author_id: str
    name: str
    tags: List[str] = []              
    age: Optional[int] = None
    created_at: Optional[str] = None
    likes: int = 0
    reply_count: int = 0

    def to_item(self) -> dict:
        return {
            "PK": f"QUESTION#{self.qid}",
            "SK": "!",
            "gsi": "Y",
            "qid": self.qid,
            "title": self.title,
            "body": self.body,
            "author": self.author_id or "unknown",
            "name": self.name or "Anonymous",
            "tags": self.tags or [],
            "age": self.age or 0,
            "date": self.created_at,
            "likes": self.likes,
            "replies": self.reply_count,
        }

    @staticmethod
    def key(qid: str) -> dict[str, str]:
        return {
            "PK": f"QUESTION#{qid}",
            "SK": "!"
        }


# ---- Conversion helper ----
def to_question(item: dict | None) -> Optional[Question]:
    if not item:
        return None

    return Question(
        qid=item.get("qid") or item.get("PK", "").replace("QUESTION#", ""),
        title=item.get("title", ""),
        body=item.get("body", ""),
        author_id=item.get("author"),
        name=item.get("name", "Anonymous"),
        tags=item.get("tags", []),
        age=item.get("age"),
        created_at=item.get("date"),
        likes=item.get("likes", 0),
        reply_count=item.get("replies", 0),
    )
