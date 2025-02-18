import json
import numpy as np

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)

    # Extract widths and heights from buildings
    widths = []
    heights = []
    building_names = []
    for building in config['buildings']:
        widths.append(building['dimensions'][0])
        heights.append(building['dimensions'][1])
        building_names.append(building['name'])

    # Extract path constraints and connections
    path_constraints = []
    connections = []
    for path in config['paths']:
        path_constraints.append([path['min_length'], path['max_length']])
        # Determine the indices of the connected buildings
        i = building_names.index(path['between'][0])
        j = building_names.index(path['between'][1])
        connections.append((i, j))

    return path_constraints, widths, heights, connections


def progress_callback(algorithm):
    # Print progress information
    n_gen = algorithm.n_gen
    n_eval = algorithm.evaluator.n_eval
    opt = algorithm.opt

    # Get the best fitness value
    best_fitness = np.min(opt.get('F'), axis=0)

    if n_gen % 10 == 0:
        print(f"Generation: {n_gen}, Evaluations: {n_eval}, Best Fitness: {best_fitness}")