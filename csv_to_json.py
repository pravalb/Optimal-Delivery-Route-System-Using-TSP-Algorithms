import csv
import json

def csv_to_json(csv_file, json_file):
    # Open the CSV file and read the data
    with open(csv_file, 'r') as csv_input:
        csv_reader = csv.DictReader(csv_input)

        # Convert CSV data to a list of dictionaries
        data = list(csv_reader)

    # Open the JSON file and write the data
    with open(json_file, 'w') as json_output:
        # Use json.dump() to write the data to the JSON file
        json.dump(data, json_output, indent=4)

# Example usage
csv_to_json('edges.csv', 'edges.json')
