import random
from evaluator import evaluate_schedule


def score_schedule(schedule: list, problem_data: dict) -> float:
    res = evaluate_schedule(schedule, problem_data)
    return res["hard_violations"] * 1000.0 + res["soft_penalty"]


def build_initial_schedule(problem_data: dict) -> list:
    courses = problem_data.get("courses", [])
    rooms = problem_data.get("rooms", [])
    timeslots = problem_data.get("timeslots", [])

    schedule = []
    for c in courses:
        room = random.choice(rooms)
        slot = random.choice(timeslots)
        schedule.append({
            "course_id": c["id"],
            "course_name": c.get("name", c["id"]),
            "faculty_id": c["faculty_id"],
            "batch_id": c["batch_id"],
            "room_id": room["id"],
            "timeslot": slot["id"] if isinstance(slot, dict) else slot,
        })
    return schedule


def generate_neighbor(schedule: list, problem_data: dict) -> list:
    rooms = problem_data.get("rooms", [])
    timeslots = problem_data.get("timeslots", [])
    n = len(schedule)
    if n == 0:
        return []

    neighbor = [dict(item) for item in schedule]
    move_type = random.randint(0, 2)

    if move_type == 0:
        idx = random.randrange(n)
        slot = random.choice(timeslots)
        neighbor[idx]["timeslot"] = slot["id"] if isinstance(slot, dict) else slot
    elif move_type == 1:
        idx = random.randrange(n)
        room = random.choice(rooms)
        neighbor[idx]["room_id"] = room["id"]
    else:
        if n >= 2:
            i, j = random.sample(range(n), 2)
            neighbor[i]["timeslot"], neighbor[j]["timeslot"] = (
                neighbor[j]["timeslot"],
                neighbor[i]["timeslot"],
            )
            neighbor[i]["room_id"], neighbor[j]["room_id"] = (
                neighbor[j]["room_id"],
                neighbor[i]["room_id"],
            )
        else:
            slot = random.choice(timeslots)
            neighbor[0]["timeslot"] = slot["id"] if isinstance(slot, dict) else slot

    return neighbor