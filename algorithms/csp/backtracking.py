import time
from csp_model import build_variables, build_domains, conflicts
from csp_utils import evaluate

def _search(variables, domains, assigned, iterations, deadline, use_forward_checking):
    if len(assigned) == len(variables):
        return True
    if time.perf_counter() >= deadline:
        return False

    # Minimum Remaining Values: choose the unassigned variable with the
    # smallest currently legal domain.
    best_var, best_values = None, None
    for var in variables:
        key = (var["course_id"], var["session_num"])
        if key in assigned:
            continue
        legal = [v for v in domains[key] if not conflicts(var, v, assigned)]
        if best_values is None or len(legal) < len(best_values):
            best_var, best_values = var, legal
    if not best_values:
        return False

    key = (best_var["course_id"], best_var["session_num"])
    for room_id, slot_id in best_values:
        if time.perf_counter() >= deadline:
            return False
        iterations[0] += 1
        assigned[key] = {
            "course_id": best_var["course_id"],
            "session_num": best_var["session_num"],
            "student_group_id": best_var["student_group_id"],
            "faculty_id": best_var["faculty_id"],
            "room_id": room_id,
            "timeslot_id": slot_id,
        }

        if use_forward_checking:
            reduced = {}
            failed = False
            for var in variables:
                vkey = (var["course_id"], var["session_num"])
                if vkey in assigned:
                    continue
                remaining = [v for v in domains[vkey] if not conflicts(var, v, assigned)]
                if not remaining:
                    failed = True
                    break
                reduced[vkey] = remaining
            if not failed:
                next_domains = dict(domains)
                next_domains.update(reduced)
                if _search(variables, next_domains, assigned, iterations, deadline, True):
                    return True
        else:
            if _search(variables, domains, assigned, iterations, deadline, False):
                return True

        del assigned[key]
    return False

def solve(problem_data: dict, timeout_sec: float = 30.0) -> dict:
    start = time.perf_counter()
    deadline = start + max(0.0, timeout_sec)
    variables = build_variables(problem_data)
    domains = build_domains(problem_data, variables)
    assigned, iterations = {}, [0]
    success = _search(variables, domains, assigned, iterations, deadline, False)
    schedule = list(assigned.values()) if success else []
    result = evaluate(schedule, problem_data)
    elapsed = (time.perf_counter() - start) * 1000
    return {
        "algorithm": "Backtracking",
        "success": success and result["hard_violations"] == 0,
        "schedule": schedule,
        "metrics": {
            "hard_violations": result["hard_violations"],
            "soft_penalty": result["soft_penalty"],
            "iterations": iterations[0],
            "execution_time_ms": round(elapsed, 2),
        },
    }
