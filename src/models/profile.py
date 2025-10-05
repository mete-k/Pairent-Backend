from pydantic import BaseModel, Field
from typing import Literal

PrivacyLevel = Literal["public", "friends", "private"]

milestones_list = [
    "First bottle feed",
    "First time drinking from a cup",
    "First time sitting without support",
    "First time crawling",
    "First time standing while holding onto something",
    "First time standing without support",
    "First tooth",
    "First solid food",
    "First steps with support",
    "First time walking",
    "First words",
    "First time pointing or gesturing",
    "First day of preschool/kindergarten",
    "Learning to ride a bike",
    "First time tying shoelaces independently",
    "First day of elementary school",
    "Learning to swim",
    "First time reading a book independently",
    "First day of middle school",
    "First day of high school",
    "Learning to drive",
    "First job",
    "Graduating high school",
    "Moving out of the family home / starting college or career"
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
    name: str | None = Field(default=None, min_length=1, max_length=100)
    dob: str | None = None
    privacy: dict[str, PrivacyLevel] | None = None
    milestones: list[dict[str, object]] | None = None


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

    def to_item(self) -> dict[str, object]:
        return {
            "PK": f"USER#{self.user_id}",
            "SK": f"CHILD#{self.child_id}#GROWTH#{self.date}",
            "child_id": self.child_id,
            "date": self.date,
            "height": self.height,
            "weight": self.weight
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
