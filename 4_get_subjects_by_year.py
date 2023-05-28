import csv
import json
from settings import OUTPUT_FOLDER_NAME

all_subjects = {}

with open("subjects.csv") as file:
    reader = csv.reader(file)
    for row in reader:
        all_subjects[row[0]] = row[2]

subjects_by_year = {}

# ENSURES THAT SUBJECT IS IN BOTH INTERNALS AND EXTERNALS
# On internals pass, Add the subject to the list
with open(f"{OUTPUT_FOLDER_NAME}/internals.json") as file:
    data = json.load(file)

    for year, subjects in data.items():
        if year not in subjects_by_year:
            subjects_by_year[year] = {}

        for subject_name in subjects:
            if subject_name not in subjects_by_year[year]:
                subjects_by_year[year][subject_name] = all_subjects[subject_name]

with open(f"{OUTPUT_FOLDER_NAME}/externals.json") as file:
    data = json.load(file)

    # On externals pass, remove subject if there is no externals data on it
    for year, subjects in subjects_by_year.items():
        for subject_name in subjects:
            if subject_name not in data[year]:
                del subjects_by_year[year][subject_name]


for year, subjects in subjects_by_year.items():
    with open(f"{OUTPUT_FOLDER_NAME}/{year}_subjects.json", 'w') as file:
        json.dump(subjects_by_year[year], file)
