# src/service/profile_service.py
from ..models.profile import (
    Profile,
    ProfileUpdate,
    Child,
    ChildCreate,
    ChildUpdate,
    Growth,
    GrowthCreate,
    Vaccine,
    VaccineCreate,
    FriendRequest,
)
from ..repo import profile_repo as repo
from typing import Any


class ProfileService:
    def __init__(self, repo):
        self.repo = repo

    # ---- Profile ----
    def create_profile(self, user_id: str, payload: dict) -> dict[str, object]:
        # Default privacy settings
        default_privacy = {
            "name": "public",
            "dob": "friends",
            "friends": "friends"
        }

        profile = Profile(
            user_id=user_id,
            name=payload["name"],
            dob=payload["dob"],
            friends=[],
            profile_privacy=default_privacy
        )
        self.repo.put_item(profile.to_item())
        return profile.model_dump()

    def get_my_profile(self, user_id: str) -> dict[str, Any]:
        profile = self.repo.get_profile(user_id)
        return profile

    def update_my_profile(self, user_id: str, payload: ProfileUpdate) -> dict[str, Any]:
        updated = self.repo.update_profile(user_id, payload.model_dump(exclude_none=True))
        return updated

    def get_user_profile(self, viewer_id: str, user_id: str) -> dict[str, Any]:
        profile = self.repo.get_profile(user_id)
        return self._apply_privacy(profile, viewer_id)

    # ---- Children ----
    def add_child(self, user_id: str, payload: ChildCreate) -> dict[str, Any]:
        child = Child(
            user_id=user_id,
            child_id=self.repo.new_child_id(user_id),
            name=payload.name,
            dob=payload.dob,
            privacy={"milestones": "public", "growth": "private", "vaccines": "friends"},
        )
        self.repo.put_item(child.to_item())
        return child.model_dump()

    def update_child(self, user_id: str, child_id: str, payload: ChildUpdate) -> dict[str, Any]:
        return self.repo.update_child(user_id, child_id, payload.model_dump(exclude_none=True))

    def delete_child(self, user_id: str, child_id: str) -> None:
        self.repo.delete_child(user_id, child_id)

    def add_growth(self, user_id: str, child_id: str, payload: GrowthCreate) -> dict[str, Any]:
        growth = Growth(
            user_id=user_id,
            child_id=child_id,
            date=payload.date,
            height=payload.height,
            weight=payload.weight,
        )
        self.repo.put_item(growth.to_item())
        return growth.model_dump()

    def add_vaccine(self, user_id: str, child_id: str, payload: VaccineCreate) -> dict[str, Any]:
        vaccine = Vaccine(
            user_id=user_id,
            child_id=child_id,
            name=payload.name,
            date=payload.date,
            status=payload.status,
        )
        self.repo.put_item(vaccine.to_item())
        return vaccine.model_dump()

    # ---- Friends ----
    def send_friend_request(self, sender_id: str, receiver_id: str) -> dict[str, Any]:
        req = FriendRequest(from_id=sender_id, to_id=receiver_id, status="pending")
        self.repo.put_item(req.to_item())
        return req.model_dump()

    def accept_friend_request(self, receiver_id: str, sender_id: str) -> dict[str, Any]:
        # delete request
        self.repo.delete_item(FriendRequest.key(receiver_id, sender_id))
        # add to each other's friend list
        self.repo.add_friend(receiver_id, sender_id)
        self.repo.add_friend(sender_id, receiver_id)
        return {"accepted": True}

    def list_friend_requests(self, user_id: str) -> list[dict[str, Any]]:
        return self.repo.get_friend_requests(user_id)

    def remove_friend(self, user_id: str, friend_id: str) -> None:
        self.repo.remove_friend(user_id, friend_id)
        self.repo.remove_friend(friend_id, user_id)

    # ---- Privacy ----
    def _apply_privacy(self, profile: dict[str, Any], viewer_id: str) -> dict[str, Any]:
        is_owner = (viewer_id == profile["user_id"])
        is_friend = viewer_id in profile.get("friends", [])

        filtered: dict[str, Any] = {}

        # profile level fields
        for field in ["name", "dob", "friends"]:
            privacy = profile["privacy"].get(field, "public")
            if privacy == "public":
                filtered[field] = profile[field]
            elif privacy == "friends" and is_friend:
                filtered[field] = profile[field]
            elif privacy == "private" and is_owner:
                filtered[field] = profile[field]

        # children (alan bazlı privacy)
        if "children" in profile:
            filtered_children = []
            for child in profile["children"]:
                child_copy: dict[str, Any] = {"id": child["child_id"], "name": child["name"]}
                for subfield in ["milestones", "growth", "vaccines"]:
                    privacy = child["privacy"].get(subfield, "public")
                    if privacy == "public":
                        child_copy[subfield] = child.get(subfield)
                    elif privacy == "friends" and is_friend:
                        child_copy[subfield] = child.get(subfield)
                    elif privacy == "private" and is_owner:
                        child_copy[subfield] = child.get(subfield)
                filtered_children.append(child_copy)
            filtered["children"] = filtered_children

        return filtered
