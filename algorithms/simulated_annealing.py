import math
import random
import time
from evaluator import evaluate_schedule
from algorithms.local_utils import (
    build_initial_schedule,
    generate_neighbor,
    score_schedule,
)


def solve(problem_data: dict, timeout_sec: float = 30.0) -> dict:
    start = time.perf_counter()
    iterations = 0

    current = build_initial_schedule(problem_data)
    current_cost = score_schedule(current, problem_data)
    best_schedule = [dict(item) for item in current]
    best_cost = current_cost

    temperature = 1000.0
    min_temperature = 0.01
    cooling_rate = 0.995

    while (time.perf_counter() - start) < timeout_sec and temperature > min_temperature:
        if best_cost == 0:
            break

        iterations += 1
        candidate = generate_neighbor(current, problem_data)
        candidate_cost = score_schedule(candidate, problem_data)
        delta = candidate_cost - current_cost

        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current = candidate
            current_cost = candidate_cost
            if current_cost < best_cost:
                best_schedule = [dict(item) for item in current]
                best_cost = current_cost

        temperature *= cooling_rate

    elapsed_ms = (time.perf_counter() - start) * 1000
    eval_result = evaluate_schedule(best_schedule, problem_data)

    return {
        "algorithm": "Simulated_Annealing",
        "success": eval_result["hard_violations"] == 0,
        "schedule": best_schedule,
        "metrics": {
            "hard_violations": eval_result["hard_violations"],
            "soft_penalty": eval_result["soft_penalty"],
            "iterations": iterations,
            "execution_time_ms": round(elapsed_ms, 2),
        },
    }