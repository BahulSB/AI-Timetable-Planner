from __future__ import annotations
from typing import Any

def get_group_id(course: dict) -> Any:
    for key in ("student_group_id", "group_id", "batch_id"):
        if key in course:
            return course[key]
    raise KeyError("Course needs student_group_id, group_id, or batch_id")

def get_id(item):
    return item["id"] if isinstance(item, dict) else item

def is_unavailable(faculty: dict, timeslot_id) -> bool:
    unavailable = faculty.get("unavailable_timeslots", faculty.get("unavailable", []))
    return timeslot_id in [get_id(x) for x in unavailable]

def room_matches(course: dict, room: dict) -> bool:
    capacity = room.get("capacity")
    enrollment = course.get("enrollment", course.get("student_count"))
    if capacity is not None and enrollment is not None and capacity < enrollment:
        return False
    required = course.get("room_type", course.get("required_room_type"))
    actual = room.get("type", room.get("room_type"))
    if required is not None and actual is not None and required != actual:
        return False
    return True

def assignment_key(a: dict):
    return (a["course_id"], a["session_num"])

def basic_hard_valid(schedule: list, problem_data: dict) -> bool:
    faculty_by_id = {x["id"]: x for x in problem_data.get("faculty", [])}
    courses_by_id = {x["id"]: x for x in problem_data.get("courses", [])}
    seen_sessions = set()
    faculty_slots, room_slots, group_slots = set(), set(), set()
    for a in schedule:
        required = {"course_id", "session_num", "student_group_id", "faculty_id", "room_id", "timeslot_id"}
        if not required.issubset(a):
            return False
        skey = (a["course_id"], a["session_num"])
        if skey in seen_sessions:
            return False
        seen_sessions.add(skey)
        slot = a["timeslot_id"]
        fkey, rkey, gkey = (a["faculty_id"], slot), (a["room_id"], slot), (a["student_group_id"], slot)
        if fkey in faculty_slots or rkey in room_slots or gkey in group_slots:
            return False
        faculty_slots.add(fkey); room_slots.add(rkey); group_slots.add(gkey)
        faculty = faculty_by_id.get(a["faculty_id"], {})
        if is_unavailable(faculty, slot):
            return False
        course = courses_by_id.get(a["course_id"], {})
        room = next((r for r in problem_data.get("rooms", []) if r["id"] == a["room_id"]), {})
        if not room_matches(course, room):
            return False
    expected = sum(int(c.get("sessions_per_week", 1)) for c in problem_data.get("courses", []))
    return len(schedule) == expected and len(seen_sessions) == expected

def evaluate(schedule: list, problem_data: dict) -> dict:
    try:
        from evaluator import evaluate_schedule
    except ImportError:
        try:
            from evaluation import evaluate_schedule
        except ImportError:
            return {"hard_violations": 0 if basic_hard_valid(schedule, problem_data) else 1,
                    "soft_penalty": 0, "breakdown": {}}
    return evaluate_schedule(schedule, problem_data)
