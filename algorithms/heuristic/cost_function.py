from typing import List, Tuple
from data import Course, Slot


Assignment = Tuple[Course, Slot]


# Penalty weights can be adjusted based on project requirements.
FACULTY_PREFERENCE_PENALTY = 5
EARLY_PERIOD_PENALTY = 2
LATE_PERIOD_PENALTY = 2
GAP_PENALTY = 3


def placement_cost(
    course: Course,
    slot: Slot,
    timetable: List[Assignment]
) -> int:
    """
    Calculate the soft-constraint penalty for one placement.

    Lower cost means a more desirable placement.
    Hard constraints are checked separately in constraints.py.
    """
    cost = 0

    # 1. Penalize a slot that is not preferred by the faculty.
    if (slot.day, slot.period) not in course.preferred_slots:
        cost += FACULTY_PREFERENCE_PENALTY

    # 2. Penalize the first and last periods slightly.
    if slot.period == min([1, slot.period]):
        cost += EARLY_PERIOD_PENALTY

    if slot.period == 6:
        cost += LATE_PERIOD_PENALTY

    # 3. Penalize gaps between classes of the same student group.
    for other_course, other_slot in timetable:
        if (
            course.student_group == other_course.student_group
            and slot.day == other_slot.day
        ):
            gap = abs(slot.period - other_slot.period) - 1
            if gap > 0:
                cost += gap * GAP_PENALTY

    return cost


def total_timetable_cost(timetable: List[Assignment]) -> int:
    """Calculate the total cost in timetable assignment order."""
    partial_timetable = []
    total = 0

    for course, slot in timetable:
        total += placement_cost(course, slot, partial_timetable)
        partial_timetable.append((course, slot))

    return total
