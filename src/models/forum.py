# src/models/forum.py
from pydantic import BaseModel

class Like(BaseModel):
    qid: str
    liked_id: str
    user_id: str

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"LIKE#{self.liked_id}",
            "qid": self.qid,
            "user_id": self.user_id,
            "liked_id": self.liked_id
        }

    def key(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"LIKE#{self.liked_id}"
        }

def to_like(item: dict | None) -> Like | None:
    if not item:
        return None
    return Like(
        user_id=item["PK"].split("#")[1],
        liked_id=item["SK"].split("#")[1],
        qid=item.get("qid", "")
    )


class Save(BaseModel):
    qid: str
    user_id: str

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f'SAVE#{self.qid}'
        }
    def key(self) -> dict[str, object]:
        return self.to_item()
def to_save(item: dict[str, str]) -> Save:
    return Save(
        user_id=item["PK"].split("#")[1],
        qid=item["SK"].split("#")[1]
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
    def key(self) -> dict[str, object]:
        return {
            "PK": f"TAG#{self.tag}",
            "SK": self.created_at
        }
def to_tag(item: dict) -> Tag | None:
    if not item:
        return None
    return Tag(
        tag=item["PK"].split("#")[1],
        created_at=item["SK"],
        qid=item["qid"]
    )