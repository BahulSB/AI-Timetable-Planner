from __future__ import annotations
from csp_utils import get_group_id, get_id, is_unavailable, room_matches

def build_variables(problem_data: dict) -> list:
    """Create one CSP variable for every required weekly course session."""
    variables = []
    for course in problem_data.get("courses", []):
        for session_num in range(1, int(course.get("sessions_per_week", 1)) + 1):
            variables.append({
                "course_id": course["id"],
                "session_num": session_num,
                "student_group_id": get_group_id(course),
                "faculty_id": course["faculty_id"],
                "course": course,
            })
    return variables

def build_domains(problem_data: dict, variables: list) -> dict:
    """Each domain contains feasible (room_id, timeslot_id) pairs."""
    rooms = problem_data.get("rooms", [])
    slots = problem_data.get("timeslots", [])
    faculty = {f["id"]: f for f in problem_data.get("faculty", [])}
    domains = {}
    for var in variables:
        f = faculty.get(var["faculty_id"], {})
        values = []
        for room in rooms:
            if not room_matches(var["course"], room):
                continue
            for slot in slots:
                slot_id = get_id(slot)
                if is_unavailable(f, slot_id):
                    continue
                values.append((room["id"], slot_id))
        domains[(var["course_id"], var["session_num"])] = values
    return domains

def conflicts(var: dict, value: tuple, assigned: dict) -> bool:
    room_id, slot_id = value
    for other in assigned.values():
        if other["timeslot_id"] != slot_id:
            continue
        if other["faculty_id"] == var["faculty_id"]:
            return True
        if other["room_id"] == room_id:
            return True
        if other["student_group_id"] == var["student_group_id"]:
            return True
    return False
