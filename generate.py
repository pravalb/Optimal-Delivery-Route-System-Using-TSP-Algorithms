import csv
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

# Read locations CSV
locations_file = 'nodes.csv'

locations = {}
with open(locations_file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        location = row['Location']
        latitude = float(row['Latitude'])
        longitude = float(row['Longitude'])
        locations[location] = (latitude, longitude)

# Create CSV file with edges and distances
edges_file = 'edges_distances.csv'

with open(edges_file, mode='w', newline='') as csv_file:
    fieldnames = ['Node1', 'Node2', 'Distance (km)']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    # Iterate through pairs of nodes and calculate distances
    node_list = list(locations.keys())
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            node1 = node_list[i]
            node2 = node_list[j]
            distance = haversine(locations[node1][0], locations[node1][1], locations[node2][0], locations[node2][1])
            writer.writerow({'Node1': node1, 'Node2': node2, 'Distance (km)': distance})

print(f"CSV file '{edges_file}' has been created with edges and distances between nodes.")
