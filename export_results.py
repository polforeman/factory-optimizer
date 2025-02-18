import json
import os
import numpy as np
from shapely import shortest_line
from shapely.geometry import LineString

def convert_results(config_file, results_file, output_file):
    # Load configuration
    with open(config_file, 'r') as file:
        config = json.load(file)

    # Load optimization results
    with open(results_file, 'r') as file:
        results = json.load(file)

    # Extract building names and dimensions from config
    building_names = [building['name'] for building in config['buildings']]
    building_dimensions = [building['dimensions'] for building in config['buildings']]

    # Extract path names and connections from config
    path_names = [path['name'] for path in config['paths']]
    path_connections = [(building_names.index(path['between'][0]), building_names.index(path['between'][1])) for path in config['paths']]

    # Prepare the results structure
    arrangements = []
    for i, (x, f, g) in enumerate(zip(results['X'], results['F'], results['G'])):
        # Reshape x to get the centers of the buildings
        centers = np.array(x).reshape(-1, 2)

        # Calculate the locations of the buildings
        buildings = []
        for j, (name, dims, center) in enumerate(zip(building_names, building_dimensions, centers)):
            buildings.append({
                "name": name,
                "location": center.tolist(),
                "dimensions": dims
            })

        # Calculate the paths
        paths = []
        for p, (name, (start_idx, end_idx)) in enumerate(zip(path_names, path_connections)):
            start_center = buildings[start_idx]['location']
            end_center = buildings[end_idx]['location']

            # Calculate the closest points on the edges of the rectangles
            start_point, end_point = closest_points_on_rectangles(start_center, end_center, buildings[start_idx]['dimensions'], buildings[end_idx]['dimensions'])

            length = np.linalg.norm(np.array(start_point) - np.array(end_point))
            paths.append({
                "name": name,
                "length": length,
                "connected_buildings": [buildings[start_idx]['name'], buildings[end_idx]['name']],
                "start_point": start_point,
                "end_point": end_point
            })

        # Calculate total area
        total_area = f[0]

        # Objectives
        objectives = {
            "objective_1": f[1],
            "objective_2": total_area
        }

        # Append the arrangement
        arrangements.append({
            "arrangement_id": i + 1,
            "buildings": buildings,
            "paths": paths,
            "total_area": total_area,
            "objectives": objectives,
            "ranking": i + 1  # Simple ranking based on index
        })

    # Save the results to a JSON file
    with open(output_file, 'w') as file:
        json.dump(arrangements, file, indent=4)


def closest_points_on_rectangles(center1, center2, dimensions1, dimensions2):
    # Calculate half widths and heights
    half_width1, half_height1 = dimensions1[0] / 2, dimensions1[1] / 2
    half_width2, half_height2 = dimensions2[0] / 2, dimensions2[1] / 2

    # Create LineStrings for the rectangles
    rect1 = LineString([
        (center1[0] - half_width1, center1[1] - half_height1),
        (center1[0] + half_width1, center1[1] - half_height1),
        (center1[0] + half_width1, center1[1] + half_height1),
        (center1[0] - half_width1, center1[1] + half_height1),
        (center1[0] - half_width1, center1[1] - half_height1)  # Close the loop
    ])

    rect2 = LineString([
        (center2[0] - half_width2, center2[1] - half_height2),
        (center2[0] + half_width2, center2[1] - half_height2),
        (center2[0] + half_width2, center2[1] + half_height2),
        (center2[0] - half_width2, center2[1] + half_height2),
        (center2[0] - half_width2, center2[1] - half_height2)  # Close the loop
    ])

    # Calculate the shortest line between the LineStrings
    shortest_line_segment = shortest_line(rect1, rect2)

    # Get the coordinates of the shortest line
    start_point = list(shortest_line_segment.coords[0])
    end_point = list(shortest_line_segment.coords[1])

    return start_point, end_point

