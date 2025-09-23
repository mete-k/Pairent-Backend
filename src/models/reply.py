# src/models/answer.py
from pydantic import BaseModel

class ReplyCreate(BaseModel):
    body: str
    parent_id: str

    class Config:
        extra = "ignore"

class Reply(BaseModel):
    qid: str
    rid: str
    parent_id: str # parent object (question or answer)
    user_id: str
    body: str
    created_at: str
    likes: int
    reply_count: int

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"QUESTION#{self.qid}",
            "SK": f"REPLY#{self.rid}",
            "parent": self.parent_id,
            "user": self.user_id,
            "body": self.body,
            "date": self.created_at,
            "likes": self.likes,
            "replies": self.reply_count
        }
    @staticmethod
    def key(qid: str, rid: str) -> dict[str, str]:
        return {
            "PK": f"QUESTION#{qid}",
            "SK": f"REPLY#{rid}"
        }

    class Config:
        extra = "ignore"
def to_reply(item: dict) -> Reply | None:
    try:
        return Reply(**item)
    except Exception as e:
        print("Error in validating reply item:", e)
        return None