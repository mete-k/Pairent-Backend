# src/models/answer.py
from pydantic import BaseModel

class Answer(BaseModel):
    qid: str
    aid: str
    parent_id: str
    user_id: str
    body: str
    created_at: str
    likes: int
    answer_count: int

    def to_item(self) -> dict[str, object]:
        # pop = 0.6 * self.answer_count + 0.4 * self.likes
        return {
            "PK": f"QUESTION#{self.qid}",
            "SK": f"ANSWER#{self.aid}",
            "parent": self.parent_id,
            "user": self.user_id,
            "body": self.body,
            "date": self.created_at,
            "likes": self.likes,
            "answers": self.answer_count
            # "popularity": pop
        }
