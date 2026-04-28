import json
from pprint import pprint

with open("dataset.json", encoding="utf-8") as f:
	d = json.load(f)

pprint([i for i in d if i["category"] == "diapers" and i["price"] < 60 and ("cheap" in i["attributes"] or "gentle" in i["attributes"])])