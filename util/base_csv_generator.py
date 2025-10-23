import pandas
import uuid

lower_limit = 1
upper_limit = 1_000_000
notification_threshold = 100_000

EXPORT_LOCATION = "../resources/base_ids.csv"

uuid_list = []
player_ids = []
statuses = []
for player_id in range(lower_limit, upper_limit + 1):
    if player_id % notification_threshold == 0:
        print(f"Processing player id: {player_id}")
    uuid_list.append(uuid.uuid4())
    player_ids.append(player_id)
    statuses.append('PENDING')

results = {
    'id': uuid_list,
    'player_id': player_ids,
    'status': statuses
}
results_df = pandas.DataFrame.from_dict(results)
print(results_df)
results_df.to_csv(EXPORT_LOCATION, index=False)
print("CSV exported...")
