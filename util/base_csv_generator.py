import pandas
import uuid
import argparse

LOG_THRESHOLD = 100_000

parser = argparse.ArgumentParser()
parser.add_argument("-l", type=int, default=1, help="Lower inclusive range limit.")
parser.add_argument("-u", type=int, default=1_000_000, help="Upper inclusive range limit.")
parser.add_argument("-o", type=str, default="../resources/base_ids.csv", help="Output file path.")
args = parser.parse_args()

uuid_list = []
player_ids = []
statuses = []
for player_id in range(args.l, args.u + 1):
    if player_id % LOG_THRESHOLD == 0:
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
results_df.to_csv(args.o, index=False)
print("CSV exported...")
