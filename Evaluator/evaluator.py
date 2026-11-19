import csv
import json
from collections import defaultdict
from typing import Any, Dict, List


def normalize_schedule(schedule: List[Dict[str, Any]], problem_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalizes schedule dictionaries across Member 1, 2, and 3 formats."""
    courses = {c["id"]: c for c in problem_data.get("courses", [])}
    normalized = []
    for item in schedule:
        c_id = item.get("course_id")
        course = courses.get(c_id, {})
        ts_id = item.get("timeslot") or item.get("timeslot_id")
        grp_id = item.get("batch_id") or item.get("student_group_id") or course.get("batch_id")
        normalized.append({
            "course_id": c_id,
            "course_name": item.get("course_name", course.get("name", c_id)),
            "faculty_id": item.get("faculty_id", course.get("faculty_id")),
            "batch_id": grp_id,
            "room_id": item.get("room_id"),
            "timeslot": ts_id,
        })
    return normalized


def evaluate_schedule(schedule: List[Dict[str, Any]], problem_data: Dict[str, Any]) -> Dict[str, Any]:
    """Central hard & soft constraint evaluator shared by all algorithms."""
    timeslots = {t["id"]: t for t in problem_data.get("timeslots", [])}
    rooms = {r["id"]: r for r in problem_data.get("rooms", [])}
    faculty = {f["id"]: f for f in problem_data.get("faculty", [])}
    batches = {b["id"]: b for b in problem_data.get("batches", [])}
    courses = {c["id"]: c for c in problem_data.get("courses", [])}

    clean_schedule = normalize_schedule(schedule, problem_data)

    breakdown = {
        "missing_or_duplicate_courses": 0,
        "faculty_clashes": 0,
        "room_clashes": 0,
        "batch_clashes": 0,
        "room_mismatch": 0,
        "faculty_unavailable": 0,
        "unpreferred_faculty_slots": 0,
        "batch_idle_gaps": 0,
        "same_course_same_day": 0,
        "late_slots": 0,
    }

    expected_ids = set(courses.keys())
    assigned_ids = [item["course_id"] for item in clean_schedule]
    breakdown["missing_or_duplicate_courses"] = (
        len(expected_ids - set(assigned_ids)) + (len(assigned_ids) - len(set(assigned_ids)))
    )

    faculty_slot_counts = defaultdict(int)
    room_slot_counts = defaultdict(int)
    batch_slot_counts = defaultdict(int)
    batch_day_periods = defaultdict(list)
    course_day_counts = defaultdict(int)

    for entry in clean_schedule:
        c_id = entry["course_id"]
        f_id = entry["faculty_id"]
        b_id = entry["batch_id"]
        r_id = entry["room_id"]
        ts_id = entry["timeslot"]

        if c_id not in courses or r_id not in rooms or ts_id not in timeslots or b_id not in batches or f_id not in faculty:
            breakdown["room_mismatch"] += 1
            continue

        course = courses[c_id]
        room = rooms[r_id]
        batch = batches[b_id]
        fac = faculty[f_id]
        ts = timeslots[ts_id]

        if room["capacity"] < batch["size"] or room["type"] != course.get("required_room_type", room["type"]):
            breakdown["room_mismatch"] += 1

        if ts_id in fac.get("unavailable_slots", fac.get("unavailable_timeslots", [])):
            breakdown["faculty_unavailable"] += 1

        faculty_slot_counts[(f_id, ts_id)] += 1
        room_slot_counts[(r_id, ts_id)] += 1
        batch_slot_counts[(b_id, ts_id)] += 1

        if ts_id not in fac.get("preferred_slots", []):
            breakdown["unpreferred_faculty_slots"] += 1

        if ts.get("is_late", False):
            breakdown["late_slots"] += 1

        batch_day_periods[(b_id, ts["day"])].append(ts["period"])
        base_code = course.get("course_code", c_id.split("_")[0])
        course_day_counts[(base_code, b_id, ts["day"])] += 1

    breakdown["faculty_clashes"] = sum(v - 1 for v in faculty_slot_counts.values() if v > 1)
    breakdown["room_clashes"] = sum(v - 1 for v in room_slot_counts.values() if v > 1)
    breakdown["batch_clashes"] = sum(v - 1 for v in batch_slot_counts.values() if v > 1)
    breakdown["same_course_same_day"] = sum(v - 1 for v in course_day_counts.values() if v > 1)

    for periods in batch_day_periods.values():
        sorted_p = sorted(periods)
        for i in range(1, len(sorted_p)):
            gap = sorted_p[i] - sorted_p[i - 1] - 1
            if gap > 0:
                breakdown["batch_idle_gaps"] += gap

    hard_violations = (
        breakdown["missing_or_duplicate_courses"]
        + breakdown["faculty_clashes"]
        + breakdown["room_clashes"]
        + breakdown["batch_clashes"]
        + breakdown["room_mismatch"]
        + breakdown["faculty_unavailable"]
    )

    soft_penalty = (
        2.0 * breakdown["unpreferred_faculty_slots"]
        + 3.0 * breakdown["batch_idle_gaps"]
        + 2.0 * breakdown["same_course_same_day"]
        + 1.0 * breakdown["late_slots"]
    )

    return {
        "hard_violations": hard_violations,
        "soft_penalty": round(soft_penalty, 2),
        "breakdown": breakdown,
    }


def print_cli_timetable(schedule: List[Dict[str, Any]], problem_data: Dict[str, Any], batch_id: str) -> None:
    """Prints a weekly timetable grid in the terminal for a specific batch."""
    clean_schedule = normalize_schedule(schedule, problem_data)
    days = problem_data["metadata"]["days"]
    periods = range(1, problem_data["metadata"]["periods_per_day"] + 1)
    ts_lookup = {t["id"]: (t["day"], t["period"]) for t in problem_data["timeslots"]}

    grid = {(d, p): "---" for d in days for p in periods}
    for item in clean_schedule:
        if item["batch_id"] == batch_id and item["timeslot"] in ts_lookup:
            day, period = ts_lookup[item["timeslot"]]
            grid[(day, period)] = f"{item['course_id']} ({item['room_id']})"

    print(f"\n=== Weekly Timetable: {batch_id} ===")
    header = f"{'Period':<8} | " + " | ".join(f"{d:<18}" for d in days)
    print(header)
    print("-" * len(header))
    for p in periods:
        row = f"P{p:<7} | " + " | ".join(f"{grid[(d, p)]:<18}" for d in days)
        print(row)


def export_schedule_csv(schedule: List[Dict[str, Any]], problem_data: Dict[str, Any], filepath: str) -> None:
    clean_schedule = normalize_schedule(schedule, problem_data)
    if not clean_schedule:
        return
    fieldnames = ["course_id", "course_name", "batch_id", "faculty_id", "room_id", "timeslot"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_schedule)


def export_schedule_json(schedule: List[Dict[str, Any]], problem_data: Dict[str, Any], filepath: str) -> None:
    clean_schedule = normalize_schedule(schedule, problem_data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_schedule, f, indent=2)