import requests
import argparse
import json
from bs4 import BeautifulSoup
from kafka import KafkaProducer

URL = "https://eu.finalfantasyxiv.com/lodestone/character/"
CHARACTER_IDS = range(1, 500)

def scrape(id: str):
    response = requests.get(url=URL + id)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {}
    data.update({"id": id})
    if soup.find(name="h1", class_="error__heading"):
        pass
    else:
        data = {}
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
            else:
                ps = detail.find_all("p")
                key = ps[0].text
                value = ps[1].text
                data.update({key: value})
    return data

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="Kafka broker IP address")
args = parser.parse_args()

producer = KafkaProducer(bootstrap_servers=args.i + ':9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for id in CHARACTER_IDS:
    data = scrape(str(id))
    producer.send("player", data)
    producer.flush()