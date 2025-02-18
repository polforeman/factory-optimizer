import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_arrangements(arrangement_file, output_dir):
    # Load arrangement results
    with open(arrangement_file, 'r') as file:
        arrangements = json.load(file)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Plot each arrangement
    for arrangement in arrangements:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal', adjustable='box')
        ax.axis('off')  # Hide the axis

        # Calculate the bounding box for all buildings
        min_x = min(b['location'][0] - b['dimensions'][0] / 2 for b in arrangement['buildings'])
        max_x = max(b['location'][0] + b['dimensions'][0] / 2 for b in arrangement['buildings'])
        min_y = min(b['location'][1] - b['dimensions'][1] / 2 for b in arrangement['buildings'])
        max_y = max(b['location'][1] + b['dimensions'][1] / 2 for b in arrangement['buildings'])

        # Plot the bounding box
        bounding_box = patches.Rectangle(
            (min_x, min_y), max_x - min_x, max_y - min_y,
            linewidth=2, edgecolor='red', facecolor='none', zorder=1
        )
        ax.add_patch(bounding_box)

        # Plot buildings
        for i, building in enumerate(arrangement['buildings']):
            location = building['location']
            dimensions = building['dimensions']
            rect = patches.Rectangle(
                (location[0] - dimensions[0] / 2, location[1] - dimensions[1] / 2),
                dimensions[0], dimensions[1], linewidth=1, edgecolor='black', facecolor='lightgrey', zorder=2
            )
            ax.add_patch(rect)
            ax.text(location[0], location[1], str(i + 1), ha='center', va='center', fontsize=12, color='black', zorder=3)

        # Plot paths
        for path in arrangement['paths']:
            start_point = path['start_point']
            end_point = path['end_point']
            length = round(path['length'], 2)  # Round the length to two decimal points
            ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 'b-', zorder=2)

            # Calculate the midpoint for the label
            mid_x = (start_point[0] + end_point[0]) / 2
            mid_y = (start_point[1] + end_point[1]) / 2
            ax.text(mid_x, mid_y, f"{length}m", ha='center', va='center', fontsize=10, color='red', rotation=45, zorder=3)

        # Display optimization values
        objectives = arrangement['objectives']
        total_area = round(arrangement['total_area'], 2)
        ax.text(min_x, max_y + 50,
                f"Total line length: {round(objectives['objective_1'], 2)} m\nBounding area: {round(objectives['objective_2'], 2)} sq m",
                ha='left', va='bottom', fontsize=12, color='black')

        # Save the plot
        plot_file = os.path.join(output_dir, f"arrangement_{arrangement['arrangement_id']}.png")
        plt.savefig(plot_file, bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
