# src/repos/question_repo.py
from flask import g
from ..db import forum_table as table
from ..models.question import Question, to_question
from ..models.forum import Like, Save, Tag
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

"""All Question persistence (DynamoDB)."""

# ---- Basic Question functionality
def create(q: Question) -> None:
    table.put_item(Item=q.to_item())
    for tag in q.tags:
        t = Tag(tag=tag, qid=q.qid, created_at=q.created_at)
        table.put_item(t.to_item())

def get_question(qid: str) -> Question | None:
    res = table.get_item(
        Key=Question.key(qid)
    )
    return to_question(res.get("Item"))

def get_forum(qid: str, all: bool) -> dict:
    res = table.query(
        KeyConditionExpression=Key("PK").eq(f"QUESTION#{qid}")
    )
    if all:
        return res
    # else, include only questions and replies; other objects are for backend use only
    items = res.get("Items")
    ret = {}
    if not items:
        return ret
    ret["Replies"] = []
    for item in items:
        sk: str = item["SK"]
        if sk == "!":
            ret["Question"] = item
        elif sk.startswith("REPLY#"):
            ret["Replies"] += item
    return ret


def edit(qid: str, title: str = "", body: str = "", tags: list[str] = []) -> None:
    # Build UpdateExpression and values
    updateExpression = ""
    expr_attr_values = {}
    expr_attr_names = {}
    if title:
        updateExpression = "SET #t = :newTitle"
        expr_attr_values[":newTitle"] = title.strip()
        expr_attr_names["#t"] = "title"
    if body:
        if updateExpression:
            updateExpression += ", #b = :newBody"
        else:
            updateExpression = "SET #b = :newBody"
        expr_attr_values[":newBody"] = body.strip()
        expr_attr_names["#b"] = "body"
    if tags:
        if updateExpression:
            updateExpression += ", #g = :newTags"
        else:
            updateExpression += "SET #g = :newTags"
        updateExpression = "SET #g = :newTags"
        expr_attr_values[":newTags"] = tags
        expr_attr_names["#g"] = "tags"

    try:
        # res = 
        table.update_item(
            Key={
                "PK": "QUESTION",
                "SK": qid
            },
            UpdateExpression=updateExpression,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            # ReturnValues="ALL_NEW"
        )
        # return to_question(res.get("Attributes"))
    except Exception as e:
        print(f"Failed to update question {qid}: {e}")
        # return None


def delete(qid: str) -> bool:
    '''
    Delete (almost) everything associated with a question.
    This includes the question itself, its replies, likes, saves, and tags.
    It does not delete save objects which are associated with the user.
    '''
    # Get all items associated with the question
    res = get_forum(qid, all=True)
    items = res.get("Items", [])
    if not items:
        return True
    
    # Add tag objects to the list of items do delete
    # This is required because tags do not share the same PK as other items
    q = get_question(qid)
    if q:
        for tag in q.tags:
            t = Tag(tag=tag, qid=q.qid, created_at=q.created_at)
            items.append(t.to_item())
    
    # Delete the items in batch
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(
                Key={
                    "PK": item["PK"],
                    "SK": item["SK"]
                }
            )
    # Continue deleting recursively
    if "LastEvaluatedKey" in res:
        delete(qid)

    # 
    return True


# ---- Like ----
def like(qid: str) -> bool:
    like = Like(qid=qid, user_id=g.user_sub, liked_id=qid)
    like_item = table.get_item(
        Key=like.key()
    ).get("Item")
    if like_item:
        return True
    
    try:
        table.update_item(
            Key=Question.key(qid),
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

def unlike(qid: str) -> bool:
    like_key = Like(qid=qid, user_id=g.user_sub, liked_id=qid).key()
    like_item = table.get_item(
        Key=like_key
    ).get("Item")
    if not like_item:
        return True
    
    try:
        table.update_item(
            Key=Question.key(qid),
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

def get_like(qid: str) -> bool:
    like = Like(qid=qid, user_id=g.user_sub, liked_id=qid)
    res = table.get_item(
        Key=like.key()
    )
    return "Item" in res

# ---- Save ----
def save_question(qid: str) -> bool:
    save = Save(qid=qid, user_id=g.user_sub)
    item = table.put_item(
        Key=save.key()
    ).get("Item")
    return item is not None
def unsave_question(qid: str) -> bool:
    key = Save(qid=qid, user_id=g.user_sub).key()
    try:
        table.delete_item(
            Key=key
        )
        return True
    except Exception as e:
        print("Error:", e)
        return False
def get_saved(qid: str) -> bool:
    key = Save(qid=qid, user_id=g.user_sub).key()
    item = table.get_item(
        Key=key
    )
    return "Item" in item
def get_saves(limit: int, last_key: dict[str, str] | None) -> dict:
    params = {
        "KeyConditionExpression": Key("PK").eq(f"USER#{g.user_sub}") 
                                & Key("SK").begins_with("SAVE"),
        "Limit": limit
    }
    if last_key:
        params["ExclusiveStartKey"] = last_key

    res = table.query(**params)
    return res
    
# ---- List ----
def list_questions(limit: int, sort: str, direction: bool, last_key: dict[str, str] | None) -> dict[str, object]:
    kwargs = {
        "IndexName": sort,
        "KeyConditionExpression": "gsi = :q",
        "ExpressionAttributeValues": {":q": "Y"},
        "ScanIndexForward": direction,  # False means greater values first
        "Limit": limit                  # => newer dates / more likes first
    }
    if last_key:
        kwargs["ExclusiveStartKey"] = last_key

    return table.query(**kwargs)


def list_questions_by_user(direction: bool, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
    kwargs = {
        "IndexName": "author",
        "KeyConditionExpression": "author = :q",
        "ExpressionAttributeValues": {":q": g.user_sub},
        "ScanIndexForward": direction,           # newer dates first
        "Limit": limit
    }
    if last_key:
        kwargs["ExclusiveStartKey"] = last_key

    return table.query(**kwargs)

def get_questions_by_qids(qids: list[str]) -> list[Question]:
    keys = [{"PK": f"QUESTION#{qid}", "SK": "META"} for qid in qids]

    res = table.meta.client.batch_get_item(
        RequestItems={
            table.name: {
                "Keys": keys
            }
        }
    )

    questions = res["Responses"].get(table.name, [])
    for i, q in enumerate(questions):
        questions[i] = to_question(q)
    return questions
