import json
import os
import random


def build_dataset(name: str, num_batches: int, num_subjects: int, seed: int = 42) -> dict:
    rng = random.Random(seed)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods_per_day = 6

    timeslots = [
        {"id": f"{d}_{p}", "day": d, "period": p, "is_late": (p == periods_per_day)}
        for d in days
        for p in range(1, periods_per_day + 1)
    ]
    all_ts_ids = [t["id"] for t in timeslots]

    num_lecture_rooms = max(2, num_batches)
    num_lab_rooms = max(1, (num_batches + 1) // 2)
    rooms = (
        [{"id": f"LH_{101 + i}", "capacity": 65, "type": "lecture"} for i in range(num_lecture_rooms)]
        + [{"id": f"LAB_{i + 1}", "capacity": 35, "type": "lab"} for i in range(num_lab_rooms)]
    )

    num_faculty = max(4, num_subjects // 2)
    faculty = []
    for i in range(num_faculty):
        unavailable = rng.sample(all_ts_ids, k=3)
        remaining = [ts for ts in all_ts_ids if ts not in unavailable]
        preferred = rng.sample(remaining, k=8)
        faculty.append({
            "id": f"F{i + 1:02d}",
            "name": f"Prof_{i + 1}",
            "unavailable_slots": unavailable,
            "unavailable_timeslots": unavailable,
            "preferred_slots": preferred,
        })

    batches = [
        {"id": f"BATCH_{i + 1}", "size": rng.choice([30, 50, 60])}
        for i in range(num_batches)
    ]

    courses = []
    for i in range(num_subjects):
        batch = batches[i % num_batches]
        fac = faculty[i % num_faculty]
        is_lab = (i % 4 == 3) and (batch["size"] <= 35)
        code = f"CS{201 + i}{'L' if is_lab else ''}"
        sessions = 1 if is_lab else rng.choice([2, 3])

        for s in range(1, sessions + 1):
            courses.append({
                "id": f"{code}_S{s}",
                "course_code": code,
                "name": f"Subject_{i + 1}_S{s}",
                "faculty_id": fac["id"],
                "batch_id": batch["id"],
                "student_group_id": batch["id"],
                "enrollment": batch["size"],
                "sessions_per_week": 1,
                "required_room_type": "lab" if is_lab else "lecture",
            })

    return {
        "metadata": {
            "dataset_name": name,
            "days": days,
            "periods_per_day": periods_per_day,
        },
        "timeslots": timeslots,
        "rooms": rooms,
        "faculty": faculty,
        "batches": batches,
        "courses": courses,
    }


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    configs = [
        ("small", 2, 5, 10),
        ("medium", 4, 12, 20),
        ("large", 6, 20, 30),
    ]
    for name, num_batches, num_subjects, seed in configs:
        dataset = build_dataset(name, num_batches, num_subjects, seed)
        path = f"data/{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2)
        print(f"Generated {path}: {len(dataset['courses'])} sessions")