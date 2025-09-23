import boto3

# Create a DynamoDB resource object pointing to local DB
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-west-2',   # any fake AWS region
    aws_access_key_id='fake',  # dummy values, required but not checked by local
    aws_secret_access_key='fake',
    endpoint_url='http://localhost:8000'
)

# Also create a low-level client for table existence checks
dynamodb_client = boto3.client(
    'dynamodb',
    region_name='us-west-2',
    aws_access_key_id='fake',
    aws_secret_access_key='fake',
    endpoint_url='http://localhost:8000'
)

forum_table = dynamodb.Table("Forum")
profile_table = dynamodb.Table("Profile")


def ensure_table():
    existing_tables = dynamodb_client.list_tables()['TableNames']

    # Forum table
    if "Forum" not in existing_tables:
        dynamodb.create_table(
            TableName="Forum",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

    # Profile table
    if "Profile" not in existing_tables:
        dynamodb.create_table(
            TableName="Profile",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

    # Wait until tables are created
    dynamodb_client.get_waiter('table_exists').wait(TableName="Forum")
    dynamodb_client.get_waiter('table_exists').wait(TableName="Profile")