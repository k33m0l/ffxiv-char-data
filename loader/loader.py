import json
import os

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ.get("TABLE_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")
FETCH_LIMIT = 1800

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    items = table.query(
        IndexName='status-index',
        KeyConditionExpression=Key("status").eq("PENDING"),
        Limit=FETCH_LIMIT
    ).get("Items", [])

    for item in items:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(item)
        )

    return {"statusCode": 200, "message": "items processed"}