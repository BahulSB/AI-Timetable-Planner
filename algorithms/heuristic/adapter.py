import os
import sys
import time

_HEURISTIC_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_HEURISTIC_DIR, "..", ".."))
for _path in (_HEURISTIC_DIR, _ROOT_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import astar
import greedy_best_first
import heuristic_function
from constraints import is_valid_assignment as _base_is_valid
from cost_function import placement_cost
from data import Course, Slot
from evaluator import evaluate_schedule
from heuristic_function import heuristic_function as _base_heuristic


def _prepare_inputs(problem_data: dict):
    ts_map = {t["id"]: t for t in problem_data["timeslots"]}
    fac_map = {f["id"]: f for f in problem_data["faculty"]}
    batch_map = {b["id"]: b for b in problem_data.get("batches", [])}

    sorted_rooms = sorted(
        problem_data["rooms"], key=lambda r: (r.get("capacity", 999), r["id"])
    )
    sorted_room_ids = [r["id"] for r in sorted_rooms]

    slots = [
        Slot(day=t["day"], period=t["period"], room=r["id"])
        for t in problem_data["timeslots"]
        for r in sorted_rooms
    ]

    courses = []
    allowed_rooms = {}
    unavailable_slots = {}

    for c in problem_data["courses"]:
        c_id = c["id"]
        fac = fac_map.get(c["faculty_id"], {})
        b_id = c.get("batch_id") or c.get("student_group_id")
        batch_size = batch_map.get(b_id, {}).get("size", c.get("enrollment", 0))
        req_type = c.get("required_room_type")

        valid_r = set()
        for r in sorted_rooms:
            if r.get("capacity", 999) < batch_size:
                continue
            if req_type and r.get("type") != req_type:
                continue
            valid_r.add(r["id"])
        allowed_rooms[c_id] = valid_r

        unavail_dp = set()
        for ts_id in fac.get("unavailable_slots", fac.get("unavailable_timeslots", [])):
            if ts_id in ts_map:
                unavail_dp.add((ts_map[ts_id]["day"], ts_map[ts_id]["period"]))
        unavailable_slots[c_id] = unavail_dp

        pref_dp = set()
        for ts_id in fac.get("preferred_slots", []):
            if ts_id in ts_map:
                pref_dp.add((ts_map[ts_id]["day"], ts_map[ts_id]["period"]))

        courses.append(
            Course(
                course_id=c_id,
                name=c.get("name", c_id),
                faculty=c["faculty_id"],
                student_group=b_id,
                preferred_slots=frozenset(pref_dp),
            )
        )

    total_ts = len(problem_data["timeslots"])
    courses.sort(
        key=lambda c: len(allowed_rooms[c.course_id]) * max(1, total_ts - len(unavailable_slots[c.course_id]))
    )
    return courses, slots, allowed_rooms, unavailable_slots, sorted_room_ids


def _run_with_full_constraints(search_fn, algo_name: str, problem_data: dict, timeout_sec: float = 10.0) -> dict:
    courses, slots, allowed_rooms, unavailable_slots, sorted_room_ids = _prepare_inputs(problem_data)
    start_time = time.perf_counter()
    deadline = start_time + max(0.1, timeout_sec)

    # Pre-filter candidate slots per course so inner loops only check legal rooms/times
    course_slots = {
        c.course_id: [
            s for s in slots
            if s.room in allowed_rooms[c.course_id]
            and (s.day, s.period) not in unavailable_slots[c.course_id]
        ]
        for c in courses
    }

    def strict_is_valid(course, slot, timetable):
        if time.perf_counter() > deadline:
            raise TimeoutError(f"{algo_name} timed out")
        valid_for_course = allowed_rooms.get(course.course_id, set())
        if slot.room not in valid_for_course:
            return False
        if (slot.day, slot.period) in unavailable_slots.get(course.course_id, set()):
            return False
        if not _base_is_valid(course, slot, timetable):
            return False

        occupied = {
            s.room for _, s in timetable if s.day == slot.day and s.period == slot.period
        }
        for r_id in sorted_room_ids:
            if r_id in valid_for_course and r_id not in occupied:
                return slot.room == r_id
        return False

    def fast_heuristic(remaining_courses, timetable, all_slots):
        if time.perf_counter() > deadline:
            raise TimeoutError(f"{algo_name} timed out")
        est = 0.0
        for course in remaining_courses:
            min_c = float("inf")
            for slot in course_slots[course.course_id]:
                if _base_is_valid(course, slot, timetable):
                    c = placement_cost(course, slot, timetable)
                    if c < min_c:
                        min_c = c
                        if min_c == 0:
                            break
            if min_c == float("inf"):
                return float("inf")
            est += min_c
        # Tie-breaker favors deeper partial schedules over shallow BFS expansion
        return est + 0.001 * len(remaining_courses)

    astar.is_valid_assignment = strict_is_valid
    greedy_best_first.is_valid_assignment = strict_is_valid
    astar.heuristic_function = fast_heuristic
    greedy_best_first.heuristic_function = fast_heuristic

    try:
        res = search_fn(courses, slots)
    except TimeoutError:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        eval_res = evaluate_schedule([], problem_data)
        return {
            "algorithm": algo_name,
            "success": False,
            "schedule": [],
            "metrics": {
                "hard_violations": eval_res["hard_violations"],
                "soft_penalty": eval_res["soft_penalty"],
                "iterations": 0,
                "execution_time_ms": elapsed_ms,
            },
        }
    finally:
        astar.is_valid_assignment = _base_is_valid
        greedy_best_first.is_valid_assignment = _base_is_valid
        astar.heuristic_function = _base_heuristic
        greedy_best_first.heuristic_function = _base_heuristic

    schedule = []
    if res.success and res.timetable:
        for course_obj, slot_obj in res.timetable:
            schedule.append({
                "course_id": course_obj.course_id,
                "course_name": course_obj.name,
                "faculty_id": course_obj.faculty,
                "batch_id": course_obj.student_group,
                "room_id": slot_obj.room,
                "timeslot": f"{slot_obj.day}_{slot_obj.period}",
            })

    eval_res = evaluate_schedule(schedule, problem_data)
    return {
        "algorithm": algo_name,
        "success": res.success and eval_res["hard_violations"] == 0,
        "schedule": schedule,
        "metrics": {
            "hard_violations": eval_res["hard_violations"],
            "soft_penalty": eval_res["soft_penalty"],
            "iterations": res.nodes_expanded,
            "execution_time_ms": round(res.execution_time * 1000, 2),
        },
    }


def solve_astar(problem_data: dict, timeout_sec: float = 10.0) -> dict:
    return _run_with_full_constraints(astar.a_star_search, "A_Star", problem_data, timeout_sec)


def solve_greedy_bfs(problem_data: dict, timeout_sec: float = 10.0) -> dict:
    return _run_with_full_constraints(
        greedy_best_first.greedy_best_first_search, "Greedy_BFS", problem_data, timeout_sec
    )