import os, time, uuid, requests
from flask import current_app
from ..models.breakroom import Breakroom
from ..repo import breakrooms_repo as repo

DAILY_API_KEY = os.environ.get("DAILY_API_KEY", "")
DAILY_SUBDOMAIN = os.environ.get("DAILY_SUBDOMAIN", "")
ROOM_TTL_SECONDS = int(os.environ.get("ROOM_TTL_SECONDS", "7200"))

def _daily_request(path, method="GET", body=None):
    url = f"https://api.daily.co/v1{path}"
    headers = {
        "Authorization": f"Bearer {DAILY_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, json=body)
    if resp.status_code >= 300:
        current_app.logger.error("Daily API error %s: %s", resp.status_code, resp.text)
        raise Exception(f"Daily API error {resp.status_code}")
    return resp.json()

def create_breakroom(owner_sub: str) -> dict:
    now = int(time.time())
    exp = now + ROOM_TTL_SECONDS
    ttl = exp + 300
    room_id = uuid.uuid4().hex[:12]
    daily_room_name = f"pairent-{room_id}"

    daily_room = _daily_request("/rooms", "POST", {
        "name": daily_room_name,
        "privacy": "private",
        "properties": {"exp": exp}
    })

    br = Breakroom(
        room_id=room_id,
        status="active",
        daily_room_name=daily_room_name,
        created_at=now,
        expires_at=exp,
        url=f"https://{DAILY_SUBDOMAIN}.daily.co/{daily_room_name}" if DAILY_SUBDOMAIN else daily_room.get("url"),
        ttl=ttl
    )

    repo.put_breakroom(br)
    repo.put_participant(room_id, owner_sub, "owner", now)

    return {"roomId": br.room_id, "url": br.url, "expiresAt": br.expires_at}

def issue_token(room_id: str, user_sub: str, username: str) -> tuple[dict | None, str | None]:
    meta = repo.get_breakroom_meta(room_id)
    if not meta:
        return None, "room_not_found"
    if meta.get("status") != "active":
        return None, "room_not_active"

    is_owner = (meta.get("owner_sub") == user_sub)
    token = _daily_request("/meeting-tokens", "POST", {
        "properties": {
            "room_name": meta["daily_room_name"],
            "is_owner": is_owner,
            "user_name": username
        }
    })

    repo.put_participant(room_id, user_sub, "owner" if is_owner else "member", int(time.time()))

    return {
        "token": token["token"],
        "roomName": meta["daily_room_name"],
        "isOwner": is_owner,
        "expiresAt": meta["exp"]
    }, None

def end_breakroom(room_id: str, requester_sub: str, requester_groups: list[str]) -> str | None:
    meta = repo.get_breakroom_meta(room_id)
    if not meta:
        return "room_not_found"
    if requester_sub != meta.get("owner_sub") and "admin" not in requester_groups:
        return "forbidden"

    _daily_request(f"/rooms/{meta['daily_room_name']}", "DELETE")
    repo.update_breakroom_status(room_id, "ended")
    return None

def get_breakroom(room_id: str) -> dict | None:
    meta = repo.get_breakroom_meta(room_id)
    if not meta:
        return None
    return {
        "roomId": room_id,
        "status": meta.get("status"),
        "ownerSub": meta.get("owner_sub"),
        "ownerName": meta.get("owner_name"),
        "createdAt": meta.get("created_at"),
        "expiresAt": meta.get("exp"),
    }

def list_breakrooms(owner_sub: str | None = None) -> list[dict]:
    items = repo.list_breakrooms(owner_sub)
    rooms = []
    for meta in items:
        rooms.append({
            "roomId": meta["PK"].replace("BRK#", ""),
            "status": meta.get("status"),
            "ownerSub": meta.get("owner_sub"),
            "ownerName": meta.get("owner_name"),
            "createdAt": meta.get("created_at"),
            "expiresAt": meta.get("exp"),
        })
    return rooms
