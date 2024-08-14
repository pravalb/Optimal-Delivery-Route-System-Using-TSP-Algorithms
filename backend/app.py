from flask import Flask, request, jsonify
from flask_cors import CORS
from itertools import permutations
import numpy as np
import json

app = Flask(__name__)
CORS(app)

# Read data from JSON files
with open('../nodes.json', 'r') as nodes_file:
    nodes_data = json.load(nodes_file)

with open('../edges.json', 'r') as edges_file:
    edges_data = json.load(edges_file)

# Extracting locations, latitude, and longitude from nodes data
# nodes_data = array of jsons
locations = [node['Location'] for node in nodes_data]
latitude = {node['Location']: float(node['Latitude']) for node in nodes_data}
longitude = {node['Location']: float(node['Longitude']) for node in nodes_data}

# Create distance matrix based on edges data
num_locations = len(locations)
distance_matrix = np.zeros((num_locations, num_locations))

for edge in edges_data:
    node1_index = locations.index(edge['Node1'])
    node2_index = locations.index(edge['Node2'])
    distance = float(edge['Distance (km)'])
    distance_matrix[node1_index, node2_index] = distance
    distance_matrix[node2_index, node1_index] = distance

# Function to calculate total distance for a given route
def calculate_total_distance(route, distance_matrix):
    total_distance = 0
    print("route", route)
    print("locations:", locations)
    for i in range(len(route) - 1):
        node1_index = locations.index(route[i])
        node2_index = locations.index(route[i + 1])
        total_distance += distance_matrix[node1_index, node2_index]
    return total_distance

# Function to perform TSP optimization using brute force
def tsp_brute_force(locations, distance_matrix):
    print("a")
    all_routes = permutations(locations)
    best_route = None
    min_distance = float('inf')

    print("b")
    for route in all_routes:
        total_distance = calculate_total_distance(route, distance_matrix)
        print("c")
        if total_distance < min_distance:
            min_distance = total_distance
            best_route = route

    print("d")
    return list(best_route)

# Function to perform TSP optimization using genetic algorithm
def tsp_genetic_algorithm(distance_matrix, population_size=50, generations=500):
    print("aa")
    num_locations = len(locations)
    population = [list(np.random.permutation(num_locations)) for _ in range(population_size)]

    print("bb")
    for gen in range(generations):
        fitness = [1 / (calculate_total_distance(route, distance_matrix) + 1) for route in population]
        idx = np.argsort(fitness)
        population = [population[i] for i in idx]
        print("cc")
        # Crossover
        crossover_point = np.random.randint(1, num_locations)
        new_population = []
        print("dd")
        for i in range(0, population_size, 2):
            parent1 = population[i]
            parent2 = population[i + 1]
            child1 = parent1[:crossover_point] + [city for city in parent2 if city not in parent1[crossover_point:]]
            child2 = parent2[:crossover_point] + [city for city in parent1 if city not in parent2[crossover_point:]]
            new_population.extend([child1, child2])

        print("ee")
        population = new_population

        # Mutation
        for i in range(population_size):
            if np.random.rand() < 0.01:
                swap_indices = np.random.choice(num_locations, 2, replace=False)
                population[i][swap_indices[0]], population[i][swap_indices[1]] = population[i][swap_indices[1]], population[i][swap_indices[0]]

    best_route = population[0]
    return best_route

# Function to perform TSP optimization using ant colony
def ant_colony_tsp(distances, n_ants=20, n_gen=100):
    pheromone = np.ones(distances.shape) / len(distances)
    all_inds = range(len(distances))

    def run():
        all_paths = gen_all_paths()
        spread_pheromone(all_paths)

    def spread_pheromone(all_paths, decay=0.95):
        pheromone_update = np.zeros(pheromone.shape)
        for path in all_paths:
            for edge in path[0]:
                pheromone_update[edge] += 1 / distances[edge]

        pheromone_update = (pheromone_update / pheromone_update.max()) * 0.1
        pheromone[:] = pheromone * (1 - decay) + pheromone_update

    def gen_all_paths():
        all_paths = []
        for i in range(n_ants):
            all_paths.append(gen_path_dist(i))
        return all_paths

    def gen_path_dist(start):
        path = []
        visited = set()
        visited.add(start)
        prev = start

        for i in range(len(distances) - 1):
            row = pheromone[prev]
            row = np.ma.masked_array(row, mask=list(visited))
            row = row ** 1
            row = row ** 2
            norm_row = row / row.sum()

            rand_val = np.random.rand()
            next_index = np.ma.masked_less_equal(norm_row.cumsum(), rand_val).argmin()

            path.append((prev, next_index))
            prev = next_index
            visited.add(prev)

        path.append((prev, start))
        distances = 0

        for edge in path:
            distances += edge[1]

        return (path, distances)

    for gen in range(n_gen):
        run()

    best_path = None
    all_time_best_path = ("placeholder", np.inf)
    total_distance = 0
    all_paths = []

    for ant_ind in range(n_ants):
        ant = gen_path_dist(0)
        total_distance += ant[1]
        all_paths.append(ant)

    if total_distance < all_time_best_path[1]:
        all_time_best_path = (total_distance, all_paths)

    return all_time_best_path

# Function to perform TSP optimization using nearest neighbor
def tsp_nearest_neighbor(locations, distance_matrix):
    current_node = locations[0]
    unvisited_nodes = set(locations[1:])
    optimized_route = [current_node]

    while unvisited_nodes:
        next_node = min(unvisited_nodes, key=lambda x: distance_matrix[locations.index(current_node), locations.index(x)])
        optimized_route.append(next_node)
        unvisited_nodes.remove(next_node)
        current_node = next_node

    return optimized_route

# Flask route to handle TSP optimization for a given unoptimized route
@app.route('/tsp/optimize_route', methods=['POST'])
def tsp_optimize_route():
    try:
        data = request.get_json()
        unoptimized_route = data.get('path', [])
        unoptimized_route = list(map(lambda x: x["id"], unoptimized_route))

        print("qqqq", unoptimized_route)
        print(1)

        # Find all edges between every set of nodes in the unoptimized route
        unoptimized_edges = []
        for i in range(len(unoptimized_route) - 1):
            node1 = unoptimized_route[i]
            node2 = unoptimized_route[i + 1]
            unoptimized_edges.append((node1, node2))

        # print(2)
        # Perform TSP optimization using brute force
        optimized_brute_force = tsp_brute_force(unoptimized_route, distance_matrix)
        print("brute", optimized_brute_force)

        # print(3)
        # # Perform TSP optimization using genetic algorithm
        # # optimized_genetic = tsp_genetic_algorithm(distance_matrix)
        #
        # print(4)
        # # Perform TSP optimization using ant colony
        # optimized_ant_colony = ant_colony_tsp(distance_matrix)
        #
        # print(5)
        # # Perform TSP optimization using nearest neighbor
        # optimized_nearest_neighbor = tsp_nearest_neighbor(unoptimized_route, distance_matrix)
        #
        # print(6)
        # Respond with the optimized routes

        response_payload = {
            'brute_force': optimized_brute_force
        }
        return jsonify(response_payload)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
