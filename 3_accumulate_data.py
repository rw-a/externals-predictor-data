import json
from settings import OUTPUT_FOLDER_NAME, JSON_DATA_NAME

with open(f"{OUTPUT_FOLDER_NAME}/{JSON_DATA_NAME}.json") as file:
    data = json.load(file)
