import json
import os
import time
from bs4 import BeautifulSoup
import requests

import boto3

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ.get("TABLE_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")
URL = "https://eu.finalfantasyxiv.com/lodestone/character/"

def scrape(player_id: str):
    data = {}
    try:
        response = requests.get(url=URL + player_id)
        if response.status_code == 404:
            pass
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            data.update({"name": soup.find(name="p", class_="frame__chara__name").text})
            data.update({"world": soup.find(name="p", class_="frame__chara__world").text})

            try:
                data.update({"title": soup.find(name="p", class_="frame__chara__title").text})
            except AttributeError:
                pass

            player_details = soup.select('div.character__profile__data__detail div.character-block__box')
            for detail in player_details:
                if detail.select('div.character__freecompany__name h4 a'):
                    fc_name = detail.select('div.character__freecompany__name h4 a')[0].text
                    data.update({"fc": fc_name})
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
        print(f"Failed scraping data for player {player_id}: {ex}")
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
            player_id = body['player_id']
            player_data = scrape(player_id)

            if not player_data:
                delete_db_row(data_id)
            else:
                upload_data(data_id, player_data)

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"]
            )
            if not player_data:
                print(f"Player id processed without results and removed: {player_id}")
            else:
                print(f"Player {player_data['name']} was processed")
        except Exception as ex:
            print(f"Failed processing message {message['MessageId']}: {ex}")
    return len(messages)

def lambda_handler(event, context):
    processed_count = 0
    for _ in range(60):
        processed_count += process_messages()
        time.sleep(1)

    return {"processed": processed_count}