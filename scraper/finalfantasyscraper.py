import json
import os
import time

import boto3

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ.get("TABLE_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")


def upload_data(data_id):
    table = dynamodb.Table(TABLE_NAME)
    table.update_item(
        Key={"id": data_id},
        UpdateExpression="set #st=:s",
        ExpressionAttributeNames={"#st": "status"},
        ExpressionAttributeValues={":s": "DONE"},
        ReturnValues="NONE"
    )

def process_messages():
    messages = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=5,
        WaitTimeSeconds=0,
        VisibilityTimeout=120
    ).get("Messages", [])

    if not messages:
        print("No messages to process")
        return 0

    for message in messages:
        try:
            body = json.loads(message["Body"])

            data_id = body['id']
            upload_data(data_id)

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"]
            )
            print(f"Player id processed: {body['player_id']}")
        except Exception as ex:
            print(f"Failed processing message {message['MessageId']}: {ex}")
    return len(messages)

def lambda_handler(event, context):
    processed_count = 0
    for _ in range(60):
        processed_count += process_messages()
        time.sleep(1)

    return {"processed": processed_count}