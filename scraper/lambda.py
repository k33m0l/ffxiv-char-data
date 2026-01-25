import asyncio
import os

import aiohttp
import boto3
from aiohttp import ClientSession
from boto3.dynamodb.conditions import Key

from scraper import scrape, URL, MAX_RATE_SECOND

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME")
MAX_RATE_MINUTE = MAX_RATE_SECOND * 60

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


async def do_task(session: ClientSession, url: str, data_id):
    data = await scrape(session, url)
    if not data:
        delete_db_row(data_id)
    else:
        upload_data(data_id, data)
    if not data:
        print(f"Player id processed without results and removed: '{url}'")
    else:
        print(f"Player {data['name']} was processed")


async def main(items):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in items:
            url = URL + item.get('player_id')
            data_id = item.get('id')

            tasks.append(
                do_task(session, url, data_id)
            )
        await asyncio.gather(*tasks, return_exceptions=True)

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    items = table.query(
        IndexName='status-index',
        KeyConditionExpression=Key("status").eq("PENDING"),
        Limit=MAX_RATE_MINUTE
    ).get("Items", [])

    if not items:
        print("No messages to process")
        return {"processed": 0}

    asyncio.run(main(items))
    return {"processed": len(items)}
