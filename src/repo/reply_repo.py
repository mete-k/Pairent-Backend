# src/repos/reply_repo.py
from flask import g
from ..db import table
from ..models.reply import Reply, to_reply
from ..models.forum import Like
from botocore.exceptions import ClientError

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

# ---- Like ----
def like(qid: str, rid: str) -> bool:
    like = Like(qid=qid, user_id=g.user_sub, liked_id=rid)
    like_item = table.get_item(
        Key=like.key()
    ).get("Item")
    if like_item:
        return True
    
    try:
        table.update_item(
            Key=Reply.key(qid, rid),
            UpdateExpression="ADD likes :inc",
            ExpressionAttributeValues={":inc": 1}
        )
        table.put_item(
            Item=like.to_item()
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise

def unlike(qid: str, rid: str) -> bool:
    like_key = Like(qid=qid, user_id=g.user_sub, liked_id=rid).key()
    like_item = table.get_item(
        Key=like_key
    ).get("Item")
    if not like_item:
        return True
    
    try:
        table.update_item(
            Key=Reply.key(qid, rid),
            UpdateExpression="ADD likes :dec",
            ExpressionAttributeValues={":dec": -1},
            ReturnValues="UPDATED_NEW"
        )
        table.delete_item(
            Key=like_key
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise

def get_like(qid: str, rid: str) -> bool:
    like = Like(qid=qid, user_id=g.user_sub, liked_id=rid)
    res = table.get_item(
        Key=like.key()
    )
    return "Item" in res