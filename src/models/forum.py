# src/models/forum.py
from pydantic import BaseModel

'''
unnecessary, this is not java
class ForumObject(BaseModel):
    def to_item(self) -> dict[str, object]: ...
    def key(self) -> dict[str, object]: ...
    def from_item(self, item: dict | None) -> self.__class__ | None: ...
'''

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
def to_save(item: dict[str, str] | None) -> Save | None:
    if not item:
        return None
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