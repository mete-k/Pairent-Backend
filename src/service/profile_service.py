# src/service/profile_service.py
from ..models.profile import (
    Profile,
    ProfileCreate,
    ProfileUpdate,
    Child,
    ChildCreate,
    ChildUpdate,
    Growth,
    GrowthCreate,
    Vaccine,
    VaccineCreate,
    FriendRequest,
    PrivacyLevel
)
from ..repo import profile_repo as repo
from ..db import table
from typing import Any
from flask import g


class ProfileService:
    def __init__(self):
        pass

    # ---- Profile ----
    def create_profile(self, payload: ProfileCreate) -> dict[str, object]:
        # Default privacy settings
        default_privacy: dict[str, PrivacyLevel] = {
            "name": "public",
            "dob": "friends",
            "friends": "friends"
        }
        profile = Profile(
            user_id=payload.user_id,
            name=payload.name,
            dob=payload.dob,
            friends=[],
            profile_privacy=default_privacy
        )
        table.put_item(profile.to_item())
        return profile.model_dump()

    def get_my_profile(self) -> dict[str, Any]:
        profile = repo.get_profile(g.user_sub)
        return profile

    def update_my_profile(self, user_id: str, payload: ProfileUpdate) -> dict[str, Any]:
        try:
            ProfileUpdate.model_validate(payload)
        except Exception as e:
            return {"error": "validation", "details": str(e)}
        updated = repo.update_profile(user_id, payload.model_dump(exclude_none=True))
        return updated

    def get_user_profile(self, viewer_id: str, user_id: str) -> dict[str, Any]:
        profile = repo.get_profile(user_id)
        return self._apply_privacy(profile, viewer_id)

    # ---- Children ----
    def add_child(self, payload: ChildCreate) -> dict[str, Any]:
        child = Child(
            user_id=g.user_sub,
            child_id=repo.new_child_id(g.user_sub),
            name=payload.name,
            dob=payload.dob,
            privacy={"milestones": "public", "growth": "private", "vaccines": "friends"},
        )
        table.put_item(child.to_item())
        return child.model_dump()

    def update_child(self, child_id: str, payload: ChildUpdate) -> dict[str, Any]:
        return repo.update_child(g.user_sub, child_id, payload.model_dump(exclude_none=True))

    def delete_child(self, child_id: str) -> None:
        repo.delete_child(g.user_sub, child_id)

    def add_growth(self, child_id: str, payload: GrowthCreate) -> dict[str, Any]:
        growth = Growth(
            user_id=g.user_sub,
            child_id=child_id,
            date=payload.date,
            height=payload.height,
            weight=payload.weight,
        )
        table.put_item(growth.to_item())
        return growth.model_dump()

    def add_vaccine(self, child_id: str, payload: VaccineCreate) -> dict[str, Any]:
        vaccine = Vaccine(
            user_id=g.user_sub,
            child_id=child_id,
            name=payload.name,
            date=payload.date,
            status=payload.status,
        )
        table.put_item(vaccine.to_item())
        return vaccine.model_dump()

    # ---- Friends ----
    def send_friend_request(self, sender_id: str, receiver_id: str) -> dict[str, Any]:
        req = FriendRequest(from_id=sender_id, to_id=receiver_id, status="pending")
        table.put_item(req.to_item())
        return req.model_dump()

    def accept_friend_request(self, receiver_id: str, sender_id: str) -> dict[str, Any]:
        # delete request
        table.delete_item(FriendRequest.key(receiver_id, sender_id))
        # add to each other's friend list
        repo.add_friend(receiver_id, sender_id)
        repo.add_friend(sender_id, receiver_id)
        return {"accepted": True}

    def list_friend_requests(self) -> list[dict[str, Any]]:
        return repo.get_friend_requests(g.user_sub)

    def remove_friend(self, friend_id: str) -> None:
        repo.remove_friend(g.user_sub, friend_id)
        repo.remove_friend(friend_id, g.user_sub)

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
