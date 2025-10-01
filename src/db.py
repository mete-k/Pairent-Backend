import boto3

# Create a DynamoDB resource object pointing to local DB
dynamodb = boto3.resource(
    'dynamodb',
    region_name='eu-north-1',
    aws_access_key_id='fake',
    aws_secret_access_key='fake',
    endpoint_url='http://127.0.0.1:8000'
)

# Also create a low-level client for table existence checks
dynamodb_client = boto3.client(
    'dynamodb',
    region_name='eu-north-1',
    aws_access_key_id='fake',
    aws_secret_access_key='fake',
    endpoint_url='http://127.0.0.1:8000'
)

table = dynamodb.Table("Pairent")

def ensure_table():
    existing_tables = dynamodb_client.list_tables()['TableNames']
    if "Pairent" not in existing_tables:
        dynamodb.create_table(
            TableName="Pairent",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "gsi", "AttributeType": "S"},
                {"AttributeName": "likes", "AttributeType": "N"},
                {"AttributeName": "date", "AttributeType": "S"},
                {"AttributeName": "author", "AttributeType": "S"},
                {"AttributeName": "sender_id", "AttributeType": "S"},   # for friend requests

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                # 1. By popularity
                {
                    "IndexName": "popular",
                    "KeySchema": [
                        {"AttributeName": "gsi", "KeyType": "HASH"},
                        {"AttributeName": "likes", "KeyType": "RANGE"}
                    ],
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": ["id", "title", "author", "tags", "date", "likes", "answers"]
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                },

                # 2. By Recency
                {
                    "IndexName": "new",
                    "KeySchema": [
                        {"AttributeName": "gsi", "KeyType": "HASH"},
                        {"AttributeName": "date", "KeyType": "RANGE"}
                    ],
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": ["id", "title", "author", "tags", "date", "likes", "answers"]
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                },

                # 3. Questions by Author
                {
                    "IndexName": "author",
                    "KeySchema": [
                        {"AttributeName": "author", "KeyType": "HASH"},
                        {"AttributeName": "date", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "INCLUDE",
                        "NonKeyAttributes": ["id", "title", "author", "tags", "date", "likes", "answers"]
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                },

                # 4. Friend requests by sender
                {
                    "IndexName": "FriendRequestsBySender",
                    "KeySchema": [
                        {"AttributeName": "sender_id", "KeyType": "HASH"},
                        {"AttributeName": "date", "KeyType": "RANGE"}
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
    }
                }
            ]
        )

    # Wait until tables are created
    dynamodb_client.get_waiter('table_exists').wait(TableName="Pairent")