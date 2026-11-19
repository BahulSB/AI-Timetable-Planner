from typing import List, Tuple
from data import Course, Slot


Assignment = Tuple[Course, Slot]


def is_valid_assignment(
    course: Course,
    slot: Slot,
    timetable: List[Assignment]
) -> bool:
    """
    Check hard constraints before adding a course to the timetable.

    Hard constraints:
    1. A faculty member cannot teach two classes at the same time.
    2. A student group cannot attend two classes at the same time.
    3. A room cannot be occupied by two classes at the same time.
    """
    for assigned_course, assigned_slot in timetable:
        same_time = (
            slot.day == assigned_slot.day
            and slot.period == assigned_slot.period
        )

        if not same_time:
            continue

        if course.faculty == assigned_course.faculty:
            return False

        if course.student_group == assigned_course.student_group:
            return False

        if slot.room == assigned_slot.room:
            return False

    return True
