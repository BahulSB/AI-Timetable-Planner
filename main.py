import json
import os
import sys

for sub in ("algorithms/csp", "algorithms/heuristic", "algorithms/local"):
    sys.path.insert(0, os.path.abspath(sub))

import backtracking
import forward_checking
import hill_climbing
import simulated_annealing
from adapter import solve_astar, solve_greedy_bfs
from evaluator import (
    evaluate_schedule,
    export_schedule_csv,
    export_schedule_json,
    print_cli_timetable,
)

ALGORITHMS = {
    "1": ("Backtracking (CSP)", backtracking.solve),
    "2": ("Forward Checking (CSP)", forward_checking.solve),
    "3": ("A* Search (Heuristic)", solve_astar),
    "4": ("Greedy Best-First Search (Heuristic)", solve_greedy_bfs),
    "5": ("Hill Climbing (Local Search)", hill_climbing.solve),
    "6": ("Simulated Annealing (Local Search)", simulated_annealing.solve),
}

DATASETS = {
    "1": "data/small.json",
    "2": "data/medium.json",
    "3": "data/large.json",
}


def main():
    print("==========================================")
    print("   COLLEGE TIMETABLE PLANNER (CLI)        ")
    print("==========================================")
    print("Select Dataset:")
    print("  1. Small  (data/small.json)")
    print("  2. Medium (data/medium.json)")
    print("  3. Large  (data/large.json)")
    ds_choice = input("Enter choice [1-3] (default 1): ").strip() or "1"
    ds_path = DATASETS.get(ds_choice, "data/small.json")

    if not os.path.exists(ds_path):
        print(f"Dataset {ds_path} missing. Run `python generate_datasets.py` first.")
        return

    with open(ds_path, "r", encoding="utf-8") as f:
        problem_data = json.load(f)

    print("\nSelect Search Algorithm:")
    for key, (label, _) in ALGORITHMS.items():
        print(f"  {key}. {label}")
    algo_choice = input("Enter choice [1-6] (default 2): ").strip() or "2"
    algo_name, solve_fn = ALGORITHMS.get(algo_choice, ALGORITHMS["2"])

    print(f"\nRunning {algo_name} on {ds_path}...")
    result = solve_fn(problem_data, timeout_sec=20.0)
    verified = evaluate_schedule(result["schedule"], problem_data)

    print("\n--- Execution Summary ---")
    print(f"Algorithm       : {result['algorithm']}")
    print(f"Success         : {result['success']}")
    print(f"Hard Violations : {verified['hard_violations']}")
    print(f"Soft Penalty    : {verified['soft_penalty']}")
    print(f"Iterations/Nodes: {result['metrics']['iterations']}")
    print(f"Execution Time  : {result['metrics']['execution_time_ms']} ms")

    if result["schedule"]:
        for batch in problem_data.get("batches", []):
            print_cli_timetable(result["schedule"], problem_data, batch["id"])

        os.makedirs("results", exist_ok=True)
        base_out = f"results/{problem_data['metadata']['dataset_name']}_{result['algorithm']}"
        export_schedule_csv(result["schedule"], problem_data, f"{base_out}.csv")
        export_schedule_json(result["schedule"], problem_data, f"{base_out}.json")
        print(f"\nExported timetable to {base_out}.csv and {base_out}.json")
    else:
        print("\nNo feasible schedule found within timeout.")


if __name__ == "__main__":
    main()