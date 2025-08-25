# src/repos/question_repo.py
from typing import Optional, List, Dict, Any
from ..db import forum_table as table, ensure_table
from ..models.question import Question, to_item, from_item

class QuestionRepo:
    """All Question persistence (DynamoDB)."""
    def __init__(self):
        ensure_table()

    def create(self, q: Question) -> None:
        table.put_item(Item=to_item(q), ConditionExpression="attribute_not_exists(PK)")

    def edit(self, qid:str, title: str = None, body: str = None) -> Optional[Question]:
        # If neither field provided, do nothing
        if not title and not body:
            return None

        # Build UpdateExpression and values
        if title and body:
            updateExpression = "SET #t = :newTitle, #b = :newBody"
            expr_attr_values = {
                ":newTitle": title.strip(),
                ":newBody": body.strip()
            }
            expr_attr_names = {"#t": "title", "#b": "body"}
        elif title and not body:
            updateExpression = "SET #t = :newTitle"
            expr_attr_values = {":newTitle": title.strip()}
            expr_attr_names = {"#t": "title"}
        elif body and not title:
            updateExpression = "SET #b = :newBody"
            expr_attr_values = {":newBody": body.strip()}
            expr_attr_names = {"#b": "body"}

        try:
            res = table.update_item(
                Key={
                    "PK": f"QUESTION#{qid}",
                    "SK": "META"
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW"
            )
            return from_item(res.get("Attributes"))
        except Exception as e:
            print(f"Failed to update question {qid}: {e}")
            return False


    def get(self, qid: str) -> Optional[Question]:
        res = table.get_item(Key={"PK": f"QUESTION#{qid}", "SK": "META"})
        return from_item(res.get("Item"))

    def list_recent(self, limit: int = 20, last_key: Optional[Dict[str, Any]] = None) -> tuple[List[Question], Optional[Dict[str, Any]]]:
        params: Dict[str, Any] = {"Limit": limit}
        if last_key:
            params["ExclusiveStartKey"] = last_key
        res = table.scan(**params)  # placeholder; later use a GSI for hot/new
        items = [from_item(i) for i in res.get("Items", [])]
        return [q for q in items if q is not None], res.get("LastEvaluatedKey")
