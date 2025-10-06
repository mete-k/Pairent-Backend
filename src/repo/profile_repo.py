# src/repo/profile_repo.py
from ..db import table
from boto3.dynamodb.conditions import Key
from ..models.profile import Profile, Child, Growth, Vaccine, FriendRequest

# ---- Profile ----
def create_profile(profile: Profile) -> dict[str, object]:
    item = profile.to_item()
    table.put_item(
        Item=item,
        ConditionExpression="attribute_not_exists(PK)" # prevent overwriting existing profile
    )
    return item

def get_profile(user_id: str) -> dict[str, object]:
    res = table.get_item(Key=Profile.key(user_id))
    return res.get("Item", {})

def update_profile(user_id: str, updates: dict):
    key = {"PK": f"USER#{user_id}", "SK": "PROFILE"}

    expr_parts = []
    names = {}
    values = {}

    for k, v in updates.items():
        names[f"#{k}"] = k
        values[f":{k}"] = v
        expr_parts.append(f"#{k} = :{k}")

    update_expr = "SET " + ", ".join(expr_parts)

    res = table.update_item(
        Key=key,
        UpdateExpression=update_expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ReturnValues="ALL_NEW"
    )

    return res["Attributes"]

# ---- Children ----
def new_child_id(user_id: str) -> str:
    import uuid
    return str(uuid.uuid4())

def add_child(user_id: str, child: dict[str, object]) -> dict[str, object]:
    table.put_item(Item=child)
    return child

def update_child(user_id: str, child_id: str, updates: dict[str, object]) -> dict[str, object]:
    from decimal import Decimal

    key = {"PK": f"USER#{user_id}", "SK": f"CHILD#{child_id}"}
    print(f"[REPO] update_child called with {user_id=} {child_id=} {updates=}")

    if not updates or not any(v is not None for v in updates.values()):
        print("[REPO] No updates provided — skipping")
        return {}

    expr_parts = []
    names = {}
    values = {}

    for k, v in updates.items():
        if isinstance(v, float):
            v = Decimal(str(v))
        if k == "milestones" and isinstance(v, list):
            cleaned = [{"id": int(m["id"]), "reached": bool(m["reached"])} for m in v]
            names["#ms"] = "milestones"
            values[":ms"] = cleaned
            expr_parts.append("#ms = :ms")
        else:
            names[f"#{k}"] = k
            values[f":{k}"] = v
            expr_parts.append(f"#{k} = :{k}")

    update_expr = "SET " + ", ".join(expr_parts)
    print("[REPO] UpdateExpression:", update_expr)
    print("[REPO] ExpressionAttributeValues:", values)

    res = table.update_item(
        Key=key,
        UpdateExpression=update_expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ReturnValues="ALL_NEW"
    )

    print("[REPO] DynamoDB update_item result:", res.get("Attributes", {}))
    return res.get("Attributes", {})

def get_children(user_id: str) -> list[dict[str, object]]:
    """Return all child records for a given user."""
    res = table.query(
        KeyConditionExpression=Key("PK").eq(f"USER#{user_id}") & Key("SK").begins_with("CHILD#")
    )
    items = res.get("Items", [])
    return [i for i in items if i["SK"].count("#") == 1]

def delete_child(user_id: str, child_id: str) -> None:
    table.delete_item(Key=Child.key(user_id, child_id))

def add_growth(growth: Growth) -> dict[str, object]:
    item = growth.to_item()
    table.put_item(Item=item)
    return item

def add_vaccine(vaccine: Vaccine) -> dict[str, object]:
    item = vaccine.to_item()
    table.put_item(Item=item)
    return item

# ---- Friends ----
def add_friend(user_id: str, friend_id: str) -> None:
    key = Profile.key(user_id)
    table.update_item(
        Key=key,
        UpdateExpression="SET friends = list_append(if_not_exists(friends, :empty), :f)",
        ExpressionAttributeValues={
            ":f": [friend_id],
            ":empty": []
        }
    )

def remove_friend(user_id: str, friend_id: str) -> None:
    # fetch current list
    profile = get_profile(user_id)
    friends: list = profile.get("friends", []) # type: ignore
    if friend_id in friends:
        friends.remove(friend_id)
        table.update_item(
            Key=Profile.key(user_id),
            UpdateExpression="SET friends = :f",
            ExpressionAttributeValues={":f": friends}
        )

# ---- Friend Requests ----
def create_friend_request(request: FriendRequest) -> dict[str, object]:
    item = request.to_item()
    table.put_item(Item=item)
    return item

def accept_friend_request(receiver_id: str, sender_id: str) -> None:
    table.delete_item(Key=FriendRequest.key(receiver_id, sender_id))

def get_friend_requests(user_id: str) -> list[dict[str, object]]:
    res = table.query(
        KeyConditionExpression=Key("PK").eq(f"USER#{user_id}") & Key("SK").begins_with("FRIEND_REQUEST#")
    )
    return res.get("Items", [])
