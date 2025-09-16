# src/models/forum.py
from pydantic import BaseModel

class Like(BaseModel):
    qid: str
    liked_id: str
    user_id: str

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"QUESTION#{self.qid}",
            "SK": f"LIKE#{self.liked_id}",
            "user": self.user_id
        }
    def key(self) -> dict[str, object]:
        return self.to_item()
def to_like(item: dict | None) -> Like | None:
    if not item:
        return None
    return Like(
        qid=item["PK"].split("#")[1],
        liked_id=item["SK"].split("#")[1],
        user_id=item["user"]
    )

class Follow(BaseModel):
    qid: str
    user_id: str

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": self.qid
        }
def to_follow(item: dict[str, str] | None) -> Follow | None:
    if not item:
        return None
    return Follow(
        qid=item["SK"],
        user_id=item["PK"].split("#")[1]
    )

class Tag(BaseModel):
    tag: str
    qid: str
    created_at: str

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"TAG#{self.tag}",
            "SK": self.created_at,
            "qid": self.qid
        }