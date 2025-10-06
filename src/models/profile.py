from pydantic import BaseModel, Field
from typing import Literal
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

PrivacyLevel = Literal["public", "friends", "private"]

milestones_list = [
    {"name": "First bottle feed", "typical": "0–3 months"},
    {"name": "First time drinking from a cup", "typical": "6–9 months"},
    {"name": "First time sitting without support", "typical": "6–8 months"},
    {"name": "First time crawling", "typical": "7–10 months"},
    {"name": "First time standing while holding onto something", "typical": "8–10 months"},
    {"name": "First time standing without support", "typical": "9–12 months"},
    {"name": "First tooth", "typical": "6–10 months"},
    {"name": "First solid food", "typical": "6 months"},
    {"name": "First steps with support", "typical": "10–12 months"},
    {"name": "First time walking", "typical": "12–15 months"},
    {"name": "First words", "typical": "12–18 months"},
    {"name": "First time pointing or gesturing", "typical": "9–14 months"},
    {"name": "First day of preschool/kindergarten", "typical": "3–5 years"},
    {"name": "Learning to ride a bike", "typical": "4–7 years"},
    {"name": "First time tying shoelaces independently", "typical": "5–7 years"},
    {"name": "First day of elementary school", "typical": "5–7 years"},
    {"name": "Learning to swim", "typical": "5–9 years"},
    {"name": "First time reading a book independently", "typical": "6–8 years"},
    {"name": "First day of middle school", "typical": "10–12 years"},
    {"name": "First day of high school", "typical": "13–15 years"},
    {"name": "Learning to drive", "typical": "16–18 years"},
    {"name": "First job", "typical": "16–20 years"},
    {"name": "Graduating high school", "typical": "17–19 years"},
    {"name": "Moving out of the family home / starting college or career", "typical": "18–22 years"},
]

# ---- Incoming payloads ----
class ProfileCreate(BaseModel):
    user_id: str
    name: str = Field(min_length=1, max_length=100)
    dob: str  # ISO format date string
    
class ProfileUpdate(BaseModel):
    profile_privacy: dict[str, PrivacyLevel] | None = None
    children: list[dict[str, object]] | None = None


class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    dob: str  # ISO format date string

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    privacy: Optional[Dict[str, str]] = None
    milestones: Optional[List[Dict[str, Any]]] = Field(default=None)

class GrowthCreate(BaseModel):
    date: str
    height: float
    weight: float


class VaccineCreate(BaseModel):
    name: str
    date: str
    status: Literal["done", "pending", "skipped"]


# ---- Primary Models ----
class Profile(BaseModel):
    user_id: str
    name: str
    dob: str
    children: list[dict[str, object]] = []
    friends: list[str]
    profile_privacy: dict[str, PrivacyLevel]

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": "PROFILE",
            "user_id": self.user_id,
            "name": self.name,
            "dob": self.dob,
            "friends": self.friends,
            "privacy": self.profile_privacy
        }

    @staticmethod
    def key(user_id: str) -> dict[str, str]:
        return {"PK": f"USER#{user_id}", "SK": "PROFILE"}


class Child(BaseModel):
    user_id: str
    child_id: str
    name: str
    dob: str
    privacy: dict[str, PrivacyLevel]
    milestones: list

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"CHILD#{self.child_id}",
            "child_id": self.child_id,
            "name": self.name,
            "dob": self.dob,
            "privacy": self.privacy,
            "milestones": self.milestones 
        }

    @staticmethod
    def key(user_id: str, child_id: str) -> dict[str, str]:
        return {"PK": f"USER#{user_id}", "SK": f"CHILD#{child_id}"}


class Growth(BaseModel):
    user_id: str
    child_id: str
    date: str
    height: float
    weight: float

    def to_item(self) -> dict:
        from decimal import Decimal
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"CHILD#{self.child_id}#GROWTH#{self.date}",
            "user_id": self.user_id,
            "child_id": self.child_id,
            "date": self.date,
            "height": Decimal(str(self.height)),
            "weight": Decimal(str(self.weight)), 
            "gsi": "GROWTH",
        }

    @staticmethod
    def key(user_id: str, child_id: str, date: str) -> dict[str, str]:
        return {"PK": f"USER#{user_id}", "SK": f"CHILD#{child_id}#GROWTH#{date}"}


class Vaccine(BaseModel):
    user_id: str
    child_id: str
    name: str
    date: str
    status: Literal["done", "pending", "skipped"]

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"CHILD#{self.child_id}#VACCINE#{self.name}",
            "child_id": self.child_id,
            "name": self.name,
            "date": self.date,
            "status": self.status
        }

    @staticmethod
    def key(user_id: str, child_id: str, name: str) -> dict[str, str]:
        return {"PK": f"USER#{user_id}", "SK": f"CHILD#{child_id}#VACCINE#{name}"}


class FriendRequest(BaseModel):
    from_id: str
    to_id: str
    status: Literal["pending", "accepted"]

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.to_id}",
            "SK": f"FRIEND_REQUEST#{self.from_id}",
            "from": self.from_id,
            "to": self.to_id,
            "status": self.status
        }

    @staticmethod
    def key(to_id: str, from_id: str) -> dict[str, str]:
        return {"PK": f"USER#{to_id}", "SK": f"FRIEND_REQUEST#{from_id}"}

from pydantic import BaseModel
from typing import Optional

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
