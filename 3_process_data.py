import json
from settings import OUTPUT_FOLDER_NAME, JSON_DATA_NAME

"""
Organises the subjects into years.
Makes the percentages cumulative (like percentiles)
"""


with open(f"{OUTPUT_FOLDER_NAME}/{JSON_DATA_NAME}.json") as file:
    data = json.load(file)

data_internals = {}
data_externals = {}

for data_type, subjects in data.items():
    for subject, subject_data in subjects.items():
        subject_name = subject[:-3]
        year = "20" + subject[-2:]

        subject_processed_data = {}

        cumulative_percentage = 0
        for raw_score, percentage in subject_data.items():
            cumulative_percentage += percentage
            subject_processed_data[raw_score] = cumulative_percentage

        # Create a pointer to the appropriate dict
        if data_type == "Internals":
            data_destination = data_internals
        else:
            data_destination = data_externals

        if year in data_destination:
            data_destination[year][subject_name] = subject_processed_data
        else:
            data_destination[year] = {subject_name: subject_processed_data}

with open(f"{OUTPUT_FOLDER_NAME}/internals.json", 'w') as file:
    json.dump(data_internals, file)

with open(f"{OUTPUT_FOLDER_NAME}/externals.json", 'w') as file:
    json.dump(data_externals, file)
