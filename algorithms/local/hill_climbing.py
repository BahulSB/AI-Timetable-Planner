import time
from evaluator import evaluate_schedule
from local_utils import (
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

    stagnant_steps = 0
    max_stagnant = 150
    neighbors_per_step = 25

    while (time.perf_counter() - start) < timeout_sec:
        if best_cost == 0:
            break

        best_neighbor = None
        best_neighbor_cost = current_cost

        for _ in range(neighbors_per_step):
            if (time.perf_counter() - start) >= timeout_sec:
                break
            iterations += 1
            candidate = generate_neighbor(current, problem_data)
            candidate_cost = score_schedule(candidate, problem_data)
            if candidate_cost < best_neighbor_cost:
                best_neighbor = candidate
                best_neighbor_cost = candidate_cost

        if best_neighbor is not None:
            current = best_neighbor
            current_cost = best_neighbor_cost
            stagnant_steps = 0
            if current_cost < best_cost:
                best_schedule = [dict(item) for item in current]
                best_cost = current_cost
        else:
            stagnant_steps += 1
            if stagnant_steps >= max_stagnant:
                current = build_initial_schedule(problem_data)
                current_cost = score_schedule(current, problem_data)
                stagnant_steps = 0

    elapsed_ms = (time.perf_counter() - start) * 1000
    eval_result = evaluate_schedule(best_schedule, problem_data)

    return {
        "algorithm": "Hill_Climbing",
        "success": eval_result["hard_violations"] == 0,
        "schedule": best_schedule,
        "metrics": {
            "hard_violations": eval_result["hard_violations"],
            "soft_penalty": eval_result["soft_penalty"],
            "iterations": iterations,
            "execution_time_ms": round(elapsed_ms, 2),
        },
    }
