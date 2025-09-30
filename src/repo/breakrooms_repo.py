from ..models.breakroom import Breakroom
from ..db import table
from boto3.dynamodb.conditions import Attr

def put_breakroom(breakroom: Breakroom):
    table.put_item(Item=breakroom.to_item())

def put_participant(room_id: str, user_sub: str, role: str, joined_at: int):
    item = {
        "PK": f"BRK#{room_id}",
        "SK": f"USER#{user_sub}",
        "joined_at": joined_at,
        "role": role,
    }
    table.put_item(Item=item)

def get_breakroom_meta(room_id: str) -> dict | None:
    res = table.get_item(Key={"PK": f"BRK#{room_id}", "SK": "META"})
    return res.get("Item")

def update_breakroom_status(room_id: str, status: str):
    table.update_item(
        Key={"PK": f"BRK#{room_id}", "SK": "META"},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": status}
    )

def list_breakrooms(owner_sub: str | None = None) -> list[dict]:
    if owner_sub:
        res = table.scan(
            FilterExpression=Attr("owner_sub").eq(owner_sub) & Attr("SK").eq("META")
        )
    else:
        res = table.scan(
            FilterExpression=Attr("SK").eq("META") & Attr("status").eq("active")
        )
    return res.get("Items", [])
