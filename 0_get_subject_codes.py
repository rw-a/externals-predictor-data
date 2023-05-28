import csv
import json
from settings import OUTPUT_FOLDER_NAME

all_subjects = {}

with open("subjects.csv") as file:
    reader = csv.reader(file)
    for row in reader:
        all_subjects[row[1]] = row[0]

with open(f"{OUTPUT_FOLDER_NAME}/subject_codes.json", 'w') as file:
    json.dump(all_subjects, file)
