import pandas
import uuid

lower_limit = 1
upper_limit = 40_000_000
notification_threshold = 100_000

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
results_df.to_csv('base_ids.csv', index=False)
print("CSV exported...")
