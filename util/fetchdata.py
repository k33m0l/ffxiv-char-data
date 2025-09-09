import boto3
import pandas
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "FFXIV"
LIMIT = 200

table = dynamodb.Table(TABLE_NAME)

def fetch_items():
    print("Fetching next batch...")
    global start_key
    global items
    if start_key is not None:
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=Key("status").eq("DONE"),
            ExclusiveStartKey=start_key,
            Limit=LIMIT,
        )
    else:
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=Key("status").eq("DONE"),
            Limit=LIMIT,
        )

    items += response.get("Items", [])
    print(f"New item count is {len(items)}")
    start_key = response.get("LastEvaluatedKey")

start_key = None
items = []
while True:
    fetch_items()
    if not start_key:
        break

df = pandas.DataFrame(items)
df.to_csv("results.csv", index=False)