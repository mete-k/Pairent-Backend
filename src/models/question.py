# src/models/question.py
from pydantic import BaseModel, Field

# Incoming payload
class QuestionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str
    tags: list[str]
    age: int

# Primary model
class Question(BaseModel):
    qid: str
    title: str
    body: str
    author_id: str
    tags: list[str]
    age: int
    created_at: str
    likes: int
    answer_count: int

    def to_item(self) -> dict:
        return {
            "PK": f"QUESTION#{self.qid}",
            "SK": "!",
            "gsi": "Y",
            "id": self.qid,
            "title": self.title,
            "body": self.body,
            "author": self.author_id,
            "tags": self.tags,
            "age": self.age,
            "date": self.created_at,
            "likes": self.likes,
            "answers": self.answer_count
        }

    @staticmethod
    def key(qid: str) -> dict[str, str]:
        return {
            "PK": f"QUESTION#{qid}",
            "SK": "!"
        }

def to_question(item: dict | None) -> Question | None:
    if not item:
        return None
    return Question(
        qid=item["id"],
        title=item["title"],
        body=item.get("body", ""),
        author_id=item["author"],
        tags=item.get("tags", []),
        age=item.get("age", 0),
        created_at=item["date"],
        likes=item.get("likes", 0),
        answer_count=item.get("answers", 0)
    )

class Tag(BaseModel):
    tag: str
    qid: int