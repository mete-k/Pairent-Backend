from typing import Optional
from pydantic import BaseModel

class Breakroom(BaseModel):
    room_id: str
    status: str
    daily_room_name: str
    created_at: int
    expires_at: int
    url: Optional[str] = None
    ttl: Optional[int] = None

    def key(self) -> dict:
        """
        Return the DynamoDB key for this breakroom.
        """
        return {"PK": "BRK", "SK": self.room_id}

    def to_item(self) -> dict:
        """
        Convert to a DynamoDB item dictionary.
        """
        item = {
            "PK": "BRK",
            "SK": self.room_id,
            "status": self.status,
            "daily_room_name": self.daily_room_name,
            "created_at": self.created_at,
            "exp": self.expires_at,
        }
        if self.url:
            item["url"] = self.url
        if self.ttl:
            item["ttl"] = self.ttl
        return item
