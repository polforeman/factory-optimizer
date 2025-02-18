import json
import os
from export_results import convert_results
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from plotting import plot_arrangements
from problem import RectanglePackingProblem
from utils import load_config, progress_callback

def main():
    # Load configuration from JSON file
    config_file = 'config.json'
    path_constraints, widths, heights, connections = load_config(config_file)

    # Create the problem instance
    problem = RectanglePackingProblem(path_constraints, widths, heights, connections)

    # Create the algorithm instance
    algorithm = NSGA2(pop_size=200)

    # Run the optimization
    res = minimize(problem, algorithm, ('n_gen', 200), verbose=False, callback=progress_callback, save_history=True)

    # Convert the results to a JSON-serializable format
    results_json = {
        'X': res.X.tolist(),  # Convert numpy arrays to lists
        'F': res.F.tolist(),
        'G': res.G.tolist() if hasattr(res, 'G') else None,
        'CV': res.CV.tolist() if hasattr(res, 'CV') else None,
        'algorithm_name': res.algorithm.__class__.__name__,
    }

    # Save the results to a JSON file
    optimization_results_path = os.path.join('Results', 'optimization_results.json')
    os.makedirs('Results', exist_ok=True)
    with open(optimization_results_path, 'w') as f:
        json.dump(results_json, f, indent=4)

    print(f"Optimization results saved to {optimization_results_path}.")

    
    arrangement_results_path = os.path.join('Results', 'arrangement_results.json')

    # Convert the results
    convert_results(config_file, optimization_results_path, arrangement_results_path)

    print(f"Arrangement results saved to {arrangement_results_path}.")
    plots_dir = os.path.join('Results', 'plots')

    # Plot the arrangements
    plot_arrangements(arrangement_results_path, plots_dir)

    print(f"Plots saved to {plots_dir}")

if __name__ == "__main__":
    main()
