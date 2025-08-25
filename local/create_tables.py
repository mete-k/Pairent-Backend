import boto3

dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-west-2",
    endpoint_url="http://localhost:8000",
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretKey"
)

try:
    table = dynamodb.Table("Forum")
    table.delete()
    table.wait_until_not_exists()
    print("Table 'Forum' deleted.")
except Exception as e:
    print(f"Table 'Forum' does not exist or could not be deleted: {e}")

table = dynamodb.create_table(
    TableName="Forum",
    KeySchema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"}
    ],
    AttributeDefinitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"}
    ],
    ProvisionedThroughput={
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5
    }
)

print("Table status: ", table.table_status)
