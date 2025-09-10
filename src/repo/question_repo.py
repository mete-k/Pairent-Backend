# src/repos/question_repo.py
from flask import g
from ..db import forum_table as table
from ..models.question import Question, to_question
from ..models.like_follow import Like, Follow
from botocore.exceptions import ClientError

class QuestionRepo:
    """All Question persistence (DynamoDB)."""
    def create(q: Question) -> None:
        table.put_item(Item=q.to_item())

    def get(qid: str) -> Question | None:
        res = table.get_item(
            Key=Question.key(qid)
        )
        return to_question(res.get("Item"))

    def edit(qid: str, title: str = None, body: str = None, tags: list[str] = None) -> Question | None:
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
            res = table.update_item(
                Key={
                    "PK": "QUESTION",
                    "SK": qid
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW"
            )
            return to_question(res.get("Attributes"))
        except Exception as e:
            print(f"Failed to update question {qid}: {e}")
            return None

    def delete(qid: str) -> bool:
        resp = table.delete_item(
            Key=Question.key(qid),
            ReturnValues="ALL_OLD"
        )
        return "Attributes" in resp
    
    def like(qid: str) -> bool:
        like = Like(qid=qid, user_id=g.user_sub)
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
        like = Like(qid=qid, user_id=g.user_sub)
        like_item = table.get_item(
            Key=like.key()
        ).get("Item")
        if not like_item:
            return True
        
        try:
            table.update_item(
                Key={
                    "PK": "QUESTION",
                    "SK": qid
                },
                UpdateExpression="ADD likes :dec",
                ExpressionAttributeValues={":dec": -1},
                ReturnValues="UPDATED_NEW"
            )
            table.delete_item(
                Key=like.key()
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise
    
    def get_like(qid: str) -> bool:
        like = Like(qid=qid, user_id=g.user_sub)
        res = table.get_item(
            Key=like.key()
        )
        return "Item" in res

    def list_questions(self, limit: int, sort: str, last_key: dict[str, str] | None) -> tuple[list[Question], dict[str, object]]:
        kwargs = {
            "IndexName": sort,
            "KeyConditionExpression": "gsi = :q",
            "ExpressionAttributeValues": {":q": "Y"},
            "ScanIndexForward": False,           # highest likes / newer dates first
            "Limit": limit
        }
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key

        return table.query(**kwargs)

    def list_questions_by_user(self, user_id: str, limit: int, last_key: dict[str, str] | None) -> dict[str, object]:
        kwargs = {
            "IndexName": "author",
            "KeyConditionExpression": "author = :q",
            "ExpressionAttributeValues": {":q": user_id},
            "ScanIndexForward": False,           # newer dates first
            "Limit": limit
        }
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key

        return table.query(**kwargs)