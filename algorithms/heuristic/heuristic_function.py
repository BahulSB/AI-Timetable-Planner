from typing import List, Tuple
from data import Course, Slot
from constraints import is_valid_assignment
from cost_function import placement_cost


Assignment = Tuple[Course, Slot]


def heuristic_function(
    remaining_courses: List[Course],
    timetable: List[Assignment],
    all_slots: List[Slot]
) -> float:
    """
    Estimate the minimum additional penalty for the courses not yet placed.

    For each remaining course, find its cheapest currently valid placement.
    The estimates are added together.

    This is an optimistic estimate because conflicts between two unassigned
    courses are not considered while calculating their individual minimums.
    """
    estimated_cost = 0

    for course in remaining_courses:
        minimum_cost = float("inf")

        for slot in all_slots:
            if is_valid_assignment(course, slot, timetable):
                cost = placement_cost(course, slot, timetable)
                minimum_cost = min(minimum_cost, cost)

        # No currently valid slot exists for this course.
        if minimum_cost == float("inf"):
            return float("inf")

        estimated_cost += minimum_cost

    return estimated_cost
