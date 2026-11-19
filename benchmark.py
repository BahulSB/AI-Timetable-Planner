import csv
import json
import os
import sys
import time

for sub in ("algorithms/csp", "algorithms/heuristic", "algorithms/local"):
    sys.path.insert(0, os.path.abspath(sub))

import backtracking
import forward_checking
import hill_climbing
import simulated_annealing
from adapter import solve_astar, solve_greedy_bfs
from evaluator import evaluate_schedule, export_schedule_csv

SOLVERS = [
    ("Backtracking", backtracking.solve),
    ("Forward_Checking", forward_checking.solve),
    ("A_Star", solve_astar),
    ("Greedy_BFS", solve_greedy_bfs),
    ("Hill_Climbing", hill_climbing.solve),
    ("Simulated_Annealing", simulated_annealing.solve),
]

DATASETS = ["data/small.json", "data/medium.json", "data/large.json"]
STOCHASTIC = {"Hill_Climbing", "Simulated_Annealing"}
TIMEOUT_SEC = 3.0


def run_benchmarks():
    os.makedirs("results/schedules", exist_ok=True)
    rows = []

    for ds_path in DATASETS:
        with open(ds_path, "r", encoding="utf-8") as f:
            problem_data = json.load(f)

        ds_name = problem_data["metadata"]["dataset_name"]
        print(f"\n================ DATASET: {ds_name.upper()} ({len(problem_data['courses'])} sessions) ================")

        for algo_name, solve_fn in SOLVERS:
            if algo_name == "A_Star" and ds_name == "large":
                print(f"{algo_name:<22} | Skipped on large dataset (state-space memory limit)")
                continue

            trials = 5 if algo_name in STOCHASTIC else 1
            successes = 0
            times, hards, softs, iters = [], [], [], []
            best_sched, best_score = None, float("inf")

            for _ in range(trials):
                t0 = time.perf_counter()
                out = solve_fn(problem_data, timeout_sec=TIMEOUT_SEC)
                wall_ms = (time.perf_counter() - t0) * 1000

                verified = evaluate_schedule(out["schedule"], problem_data)
                h, s = verified["hard_violations"], verified["soft_penalty"]
                if h == 0 and len(out["schedule"]) == len(problem_data["courses"]):
                    successes += 1

                times.append(out["metrics"].get("execution_time_ms", wall_ms))
                hards.append(h)
                softs.append(s)
                iters.append(out["metrics"].get("iterations", 0))

                if (h * 1000 + s) < best_score:
                    best_score = h * 1000 + s
                    best_sched = out["schedule"]

            if best_sched:
                export_schedule_csv(best_sched, problem_data, f"results/schedules/{ds_name}_{algo_name}.csv")

            row = {
                "Dataset": ds_name,
                "Sessions": len(problem_data["courses"]),
                "Algorithm": algo_name,
                "Trials": trials,
                "Success_Rate_%": round((successes / trials) * 100, 1),
                "Avg_Time_ms": round(sum(times) / len(times), 2),
                "Avg_Hard_Violations": round(sum(hards) / len(hards), 2),
                "Best_Soft_Penalty": round(min(softs), 2),
                "Avg_Soft_Penalty": round(sum(softs) / len(softs), 2),
                "Avg_Iterations": round(sum(iters) / len(iters), 1),
            }
            rows.append(row)
            print(
                f"{row['Algorithm']:<22} | Success: {row['Success_Rate_%']:>5}% | "
                f"Time: {row['Avg_Time_ms']:>8} ms | Hard: {row['Avg_Hard_Violations']:>5} | "
                f"Best Soft: {row['Best_Soft_Penalty']:>6} | Iters: {row['Avg_Iterations']}"
            )

    out_csv = "results/benchmark_summary.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved benchmark report table to {out_csv}")


if __name__ == "__main__":
    run_benchmarks()
