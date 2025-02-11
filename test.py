import json

with open("queries.json", "r") as f:
    data = json.load(f)
    print(data)

for item in data:
    print(data[item]["influx"])
    