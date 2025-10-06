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
    PrivacyLevel,
    milestones_list,
)
from ..repo import profile_repo as repo
from ..db import table
from typing import Any
from flask import g, current_app

class ProfileService:
    def __init__(self):
        pass

    # ---- Profile ----
    def create_profile(self, payload: ProfileCreate) -> dict[str, object]:
        default_privacy: dict[str, PrivacyLevel] = {
            "name": "public",
            "dob": "friends",
            "friends": "friends",
            "children": "friends",
        }
        profile = Profile(
            user_id=payload.user_id,
            name=payload.name,
            dob=payload.dob,
            friends=[],
            profile_privacy=default_privacy,
        )
        table.put_item(Item=profile.to_item())
        return profile.model_dump()

    def get_my_profile(self) -> dict[str, Any]:
        print("DEBUG /profile/me user_sub:", g.user_sub)
        profile = repo.get_profile(g.user_sub)
        print("DEBUG retrieved:", profile)
        return profile

    def update_profile(self, payload: dict):
        """Update current user's profile fields like name, bio, or privacy."""
        return repo.update_profile(g.user_sub, payload)

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
            milestones=[{"id": i, "reached": False} for i in range(len(milestones_list))],
        )
        table.put_item(Item=child.to_item())
        return child.model_dump()


    def update_child(self, child_id: str, payload: ChildUpdate | dict[str, Any]) -> dict[str, Any]:
        """Update a child's record (milestones, name, etc.)."""
        # --- Handle both dict or pydantic model inputs ---
        if isinstance(payload, dict):
            updates = payload
        else:
            updates = payload.model_dump(exclude_none=True)

        # --- If milestones came through raw JSON but Pydantic stripped them ---
        # force-include if request payload has them in request.json
        from flask import request
        req_json = request.get_json(silent=True) or {}
        if "milestones" in req_json and "milestones" not in updates:
            updates["milestones"] = req_json["milestones"]

        print(f"[SERVICE] update_child for {child_id}: {updates}")

        if not updates:
            print("[SERVICE] No valid updates found — skipping")
            return {}

        result = repo.update_child(g.user_sub, child_id, updates)
        print(f"[SERVICE] DynamoDB updated child {child_id}")
        return result

    def delete_child(self, child_id: str) -> None:
        repo.delete_child(g.user_sub, child_id)

    def list_children(self) -> list[dict[str, Any]]:
        """Return all children for the current user."""
        children = repo.get_children(g.user_sub)
        return children

    # ---- Growth ----
    def add_growth(self, child_id: str, payload: GrowthCreate) -> dict[str, Any]:
        growth = Growth(
            user_id=g.user_sub,
            child_id=child_id,
            date=payload.date,
            height=payload.height,
            weight=payload.weight,
        )
        table.put_item(Item=growth.to_item())
        return growth.model_dump()

    def list_growth(self, child_id: str) -> list[dict]:
        """Return all growth records for the child."""
        from boto3.dynamodb.conditions import Key

        res = table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{g.user_sub}")
            & Key("SK").begins_with(f"CHILD#{child_id}#GROWTH#")
        )
        return res.get("Items", [])

    # ---- Vaccines ----
    def add_vaccine(self, child_id: str, payload: VaccineCreate) -> dict[str, Any]:
        vaccine = Vaccine(
            user_id=g.user_sub,
            child_id=child_id,
            name=payload.name,
            date=payload.date,
            status=payload.status,
        )
        table.put_item(Item=vaccine.to_item())
        return vaccine.model_dump()

    def list_vaccine(self, child_id: str) -> list[dict]:
        """Return all vaccine records for the child."""
        from boto3.dynamodb.conditions import Key

        res = table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{g.user_sub}")
            & Key("SK").begins_with(f"CHILD#{child_id}#VACCINE#")
        )
        return res.get("Items", [])

    # ---- Milestones ----
    def list_milestones(self, child_id: str) -> list[dict]:
        """Return milestone progress for the child."""
        from decimal import Decimal
        from boto3.dynamodb.conditions import Key
        from ..models.profile import milestones_list

        # Get the child record from DynamoDB
        res = table.get_item(Key={"PK": f"USER#{g.user_sub}", "SK": f"CHILD#{child_id}"})
        item = res.get("Item", {})

        milestones = item.get("milestones", [])

        result = []
        for m in milestones:
            try:
                # Convert Decimal or string ID to int
                mid = int(m["id"]) if not isinstance(m["id"], int) else m["id"]
                milestone_def = milestones_list[mid]

                result.append({
                    "id": mid,
                    "name": milestone_def["name"],
                    "typical": milestone_def["typical"],
                    "done": bool(m.get("reached", False))
                })
            except (IndexError, KeyError, TypeError, ValueError) as e:
                print(f"[WARN] Skipping invalid milestone entry: {m} ({e})")
                continue

        return result
    
    def toggle_milestone(self, child_id: str, milestone_id: int) -> dict[str, Any]:
        """Toggle a milestone's 'reached' status for a child."""
        from boto3.dynamodb.conditions import Key
        from decimal import Decimal

        # Fetch the child record
        res = table.get_item(Key={"PK": f"USER#{g.user_sub}", "SK": f"CHILD#{child_id}"})
        item = res.get("Item")

        if not item:
            return {"error": "Child not found"}, 404

        milestones = item.get("milestones", [])
        updated = False

        # Convert milestone_id to int (Decimal-safe)
        target_id = int(milestone_id)

        for m in milestones:
            mid = int(m["id"]) if isinstance(m["id"], Decimal) else m["id"]
            if mid == target_id:
                m["reached"] = not m.get("reached", False)
                updated = True
                break

        if not updated:
            return {"error": "Milestone not found"}, 404

        # Write the updated milestones array back
        table.update_item(
            Key={"PK": f"USER#{g.user_sub}", "SK": f"CHILD#{child_id}"},
            UpdateExpression="SET milestones = :m",
            ExpressionAttributeValues={":m": milestones},
        )

        return {"ok": True, "milestone_id": target_id, "new_state": m["reached"]}

    # ---- Friends ----
    def send_friend_request(self, sender_id: str, receiver_id: str) -> dict[str, Any]:
        req = FriendRequest(from_id=sender_id, to_id=receiver_id, status="pending")
        table.put_item(Item=req.to_item())
        return req.model_dump()

    def accept_friend_request(self, receiver_id: str, sender_id: str) -> dict[str, Any]:
        table.delete_item(FriendRequest.key(receiver_id, sender_id))
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
        is_owner = viewer_id == profile["user_id"]
        is_friend = viewer_id in profile.get("friends", [])
        filtered: dict[str, Any] = {}

        for field in ["name", "dob", "friends"]:
            privacy = profile["privacy"].get(field, "public")
            if privacy == "public":
                filtered[field] = profile[field]
            elif privacy == "friends" and is_friend:
                filtered[field] = profile[field]
            elif privacy == "private" and is_owner:
                filtered[field] = profile[field]

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
