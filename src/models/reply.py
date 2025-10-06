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
    name: str
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
            "name": self.name,
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
        return Reply(
            qid=item["PK"].split("#", 1)[1],
            rid=item["SK"].split("#", 1)[1],
            parent_id=item.get("parent", ""),
            user_id=item.get("user", ""),
            body=item.get("body", ""),
            name=item.get("name", "Anonymous"),
            created_at=item.get("date", ""),
            likes=item.get("likes", 0),
            reply_count=item.get("replies", 0)
        )
    except Exception as e:
        print("Error in validating reply item:", e)
        return None