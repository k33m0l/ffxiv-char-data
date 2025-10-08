import asyncio
import json
import os

import aiohttp
import boto3
from aiohttp import ClientSession
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ.get("TABLE_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")

MAX_RATE_MINUTE = 300
MAX_RATE_SECOND = 5
TIME_LIMIT_SECONDS = 1
rate_limit = AsyncLimiter(MAX_RATE_SECOND, TIME_LIMIT_SECONDS)
URL = "https://eu.finalfantasyxiv.com/lodestone/character/"


async def scrape(session: ClientSession, url: str):
    async with rate_limit:
        async with session.get(url) as response:
            data = {}
            try:
                if response.status == 404:
                    pass
                else:
                    website_text = await response.text()
                    soup = BeautifulSoup(website_text, "html.parser")
                    data.update({"name": soup.find(name="p", class_="frame__chara__name").text})
                    data.update({"world": soup.find(name="p", class_="frame__chara__world").text})

                    # Title may not always be set for the player
                    try:
                        data.update({"title": soup.find(name="p", class_="frame__chara__title").text})
                    except AttributeError:
                        pass

                    player_details = soup.select('div.character__profile__data__detail div.character-block__box')
                    for detail in player_details:
                        # Free company is optional data and has a different tag
                        if detail.select('div.character__freecompany__name h4 a'):
                            fc_name = detail.select('div.character__freecompany__name h4 a')[0].text
                            data.update({"fc": fc_name})
                        # PVP team is optional data and has a different tag
                        elif detail.select('div.character__pvpteam__name h4 a'):
                            pvp_name = detail.select('div.character__pvpteam__name h4 a')[0].text
                            data.update({"pvp": pvp_name})
                        else:
                            ps = detail.find_all("p")
                            key = ps[0].text
                            value = ps[1].text
                            data.update({key: value})

                    player_levels = soup.select('div.character__level__list ul li')
                    for player_level_element in player_levels:
                        player_level = player_level_element.text
                        player_class = player_level_element.find('img')['data-tooltip']
                        data.update({player_class: player_level})
            except Exception as ex:
                print(f"Failed scraping data for url: '{url}': {ex}")
                data.update({"error": "scraping error"})
            return data


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
