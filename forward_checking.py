import time
from csp_model import build_variables, build_domains, conflicts
from csp_utils import evaluate
from backtracking import _search

def solve(problem_data: dict, timeout_sec: float = 30.0) -> dict:
    start = time.perf_counter()
    deadline = start + max(0.0, timeout_sec)
    variables = build_variables(problem_data)
    domains = build_domains(problem_data, variables)
    assigned, iterations = {}, [0]
    success = _search(variables, domains, assigned, iterations, deadline, True)
    schedule = list(assigned.values()) if success else []
    result = evaluate(schedule, problem_data)
    elapsed = (time.perf_counter() - start) * 1000
    return {
        "algorithm": "Forward_Checking",
        "success": success and result["hard_violations"] == 0,
        "schedule": schedule,
        "metrics": {
            "hard_violations": result["hard_violations"],
            "soft_penalty": result["soft_penalty"],
            "iterations": iterations[0],
            "execution_time_ms": round(elapsed, 2),
        },
    }
