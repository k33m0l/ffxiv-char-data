import asyncio
import json
import os
from scraper import scrape, URL

import aiohttp
import boto3
from aiohttp import ClientSession

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ.get("TABLE_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")

MAX_RATE_MINUTE = 300

def upload_data(data_id, player_data):
    try:
        table = dynamodb.Table(TABLE_NAME)
        update_expression = "set #st=:s, " + ", ".join(f"#k{i}=:v{i}" for i in range(len(player_data)))
        expr_attr_names = {"#st": "status"}
        expr_attr_names.update({f"#k{i}": key for i, key in enumerate(player_data.keys())})
        expr_attr_values = {":s": "DONE"}
        expr_attr_values.update({f":v{i}": value for i, value in enumerate(player_data.values())})
        table.update_item(
            Key={"id": data_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="NONE"
        )
    except Exception as ex:
        print(f"Failed uploading data id {data_id}: {ex}")


def delete_db_row(data_id):
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.delete_item(
            Key={"id": data_id}
        )
    except Exception as ex:
        print(f"Failed deleting data with id {data_id}: {ex}")


async def do_task(session: ClientSession, url: str, data_id, sqs_handle):
    data = await scrape(session, url)
    if not data:
        delete_db_row(data_id)
    else:
        upload_data(data_id, data)
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=sqs_handle
    )
    if not data:
        print(f"Player id processed without results and removed: '{url}'")
    else:
        print(f"Player {data['name']} was processed")


async def main(messages):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for message in messages:
            json_message = json.loads(message["Body"])
            url = URL + json_message['player_id']
            data_id = json_message['id']
            sqs_handle = message["ReceiptHandle"]

            tasks.append(
                do_task(session, url, data_id, sqs_handle)
            )
        await asyncio.gather(*tasks, return_exceptions=True)


def lambda_handler(event, context):
    messages = []
    while len(messages) < MAX_RATE_MINUTE:
        messages.extend(
            sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=0,
                VisibilityTimeout=120
            ).get("Messages", [])
        )
        if not messages:
            print("No messages to process")
            return {"processed": 0}

    asyncio.run(main(messages))
    return {"processed": len(messages)}
