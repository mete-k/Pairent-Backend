# src/repos/reply_repo.py
from flask import g
from ..db import forum_table as table
from ..models.reply import Reply, to_reply

def create(reply: Reply) -> None:
    table.put_item(Item=reply.to_item())

def get_reply(qid: str, rid: str) -> Reply | None:
    res = table.get_item(
        Key={"PK": f"QUESTION#{qid}", "SK": f"REPLY#{rid}"}
    )
    return to_reply(res.get("Item"))

def edit(qid: str, rid: str, body: str = "") -> None:
    if not body:
        return
    try:
        table.update_item(
            Key={"PK": f"QUESTION#{qid}", "SK": f"REPLY#{rid}"},
            UpdateExpression="SET #b = :newBody",
            ExpressionAttributeNames={"#b": "body"},
            ExpressionAttributeValues={":newBody": body.strip()},
        )
    except Exception as e:
        print(f"Failed to update reply {rid}: {e}")

def delete(qid: str, rid: str) -> bool:
    try:
        table.delete_item(
            Key={"PK": f"QUESTION#{qid}", "SK": f"REPLY#{rid}"}
        )
        return True
    except Exception as e:
        print(f"Failed to delete reply {rid}: {e}")
        return False