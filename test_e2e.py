import os
import sys

for sub in ("algorithms/csp", "algorithms/heuristic", "algorithms/local"):
    sys.path.insert(0, os.path.abspath(sub))

import backtracking
import forward_checking
import hill_climbing
import simulated_annealing
from adapter import solve_astar, solve_greedy_bfs
from evaluator import evaluate_schedule, export_schedule_csv, export_schedule_json
from generate_datasets import build_dataset


def test_end_to_end():
    problem_data = build_dataset("e2e_test", num_batches=2, num_subjects=3, seed=42)
    solvers = [
        ("Backtracking", backtracking.solve),
        ("Forward_Checking", forward_checking.solve),
        ("A_Star", solve_astar),
        ("Greedy_BFS", solve_greedy_bfs),
        ("Hill_Climbing", hill_climbing.solve),
        ("Simulated_Annealing", simulated_annealing.solve),
    ]

    os.makedirs("results/test_tmp", exist_ok=True)
    for name, fn in solvers:
        res = fn(problem_data, timeout_sec=10.0)
        assert "schedule" in res and "metrics" in res, f"{name} missing required keys"
        verified = evaluate_schedule(res["schedule"], problem_data)
        print(f"[PASS] {name:<20} -> Hard: {verified['hard_violations']}, Soft: {verified['soft_penalty']}")

        if res["schedule"]:
            export_schedule_csv(res["schedule"], problem_data, f"results/test_tmp/{name}.csv")
            export_schedule_json(res["schedule"], problem_data, f"results/test_tmp/{name}.json")
            assert os.path.exists(f"results/test_tmp/{name}.csv")
            assert os.path.exists(f"results/test_tmp/{name}.json")

    print("\nAll 6 solvers and export pipelines passed end-to-end verification.")


if __name__ == "__main__":
    test_end_to_end()
