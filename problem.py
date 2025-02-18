from pymoo.core.problem import Problem
import numpy as np
from shapely.geometry import Polygon, LineString

class RectanglePackingProblem(Problem):
    def __init__(self, path_min_max, widths, heights, connections):
        super().__init__(n_var=8, n_obj=2, n_constr=3, xl=-10000, xu=10000)
        self.widths = widths
        self.heights = heights
        self.path_min_max = path_min_max  # Store path constraints
        self.connections = connections  # Store connections between buildings
        self.constraint_violations = []  # Custom array to store constraint violations

    def _evaluate(self, x, out, *args, **kwargs):
        centers = x.reshape(-1, 4, 2)
        half_widths = np.array(self.widths) / 2
        half_heights = np.array(self.heights) / 2

        min_x = np.min(centers[:, :, 0] - half_widths[np.newaxis, :], axis=1)
        max_x = np.max(centers[:, :, 0] + half_widths[np.newaxis, :], axis=1)
        min_y = np.min(centers[:, :, 1] - half_heights[np.newaxis, :], axis=1)
        max_y = np.max(centers[:, :, 1] + half_heights[np.newaxis, :], axis=1)

        bounding_box_area = (max_x - min_x) * (max_y - min_y)

        # Initialize the output dictionary
        out["F"] = np.zeros((x.shape[0], self.n_obj))
        out["G"] = np.zeros((x.shape[0], self.n_constr))

        out["F"][:, 0] = bounding_box_area

        # Calculate path lengths as the closest distance between connected rectangles
        path_lengths = np.zeros((x.shape[0], len(self.connections)))
        for k in range(x.shape[0]):
            for p, (i, j) in enumerate(self.connections):
                rect1 = (centers[k, i, 0], centers[k, i, 1], half_widths[i], half_heights[i])
                rect2 = (centers[k, j, 0], centers[k, j, 1], half_widths[j], half_heights[j])
                closest_distance = self.closest_distance_between_rectangles(rect1, rect2)
                path_lengths[k, p] = closest_distance

        total_path_length = np.sum(path_lengths, axis=1)
        out["F"][:, 1] = total_path_length

        # Constraints
        constraint_violation = np.zeros((x.shape[0], 3))
        for k in range(x.shape[0]):
            for i in range(len(self.widths)):
                for j in range(i + 1, len(self.widths)):
                    rect1 = (centers[k, i, 0], centers[k, i, 1], half_widths[i], half_heights[i])
                    rect2 = (centers[k, j, 0], centers[k, j, 1], half_widths[j], half_heights[j])

                    # Distance-based check
                    if not self.rectangles_might_intersect(rect1, rect2):
                        continue

                    # AABB check
                    if self.rectangles_intersect_aabb(rect1, rect2):
                        constraint_violation[k, 0] += 1

            # Path length constraints
            for p in range(len(self.connections)):
                if path_lengths[k, p] < self.path_min_max[p][0] or path_lengths[k, p] > self.path_min_max[p][1]:
                    constraint_violation[k, p + 1] += 1

        self.constraint_violations.append(constraint_violation.copy())  # Save to custom array
        out["G"] = constraint_violation

    def rectangles_might_intersect(self, rect1, rect2):
        # rect = (center_x, center_y, half_width, half_height)
        distance = np.hypot(rect1[0] - rect2[0], rect1[1] - rect2[1])
        max_distance = (np.hypot(rect1[2], rect1[3]) + np.hypot(rect2[2], rect2[3]))
        return distance < max_distance

    def rectangles_intersect_aabb(self, rect1, rect2):
        # rect = (center_x, center_y, half_width, half_height)
        return (abs(rect1[0] - rect2[0]) < (rect1[2] + rect2[2]) and
                abs(rect1[1] - rect2[1]) < (rect1[3] + rect2[3]))

    def closest_distance_between_rectangles(self, rect1, rect2):
        # rect = (center_x, center_y, half_width, half_height)
        dx = abs(rect1[0] - rect2[0]) - (rect1[2] + rect2[2])
        dy = abs(rect1[1] - rect2[1]) - (rect1[3] + rect2[3])
        if dx < 0 and dy < 0:
            return 0  # Rectangles overlap
        return max(dx, dy, 0)
