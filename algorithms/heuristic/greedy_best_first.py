import heapq
import itertools
import time
from typing import List, Tuple

from data import Course, Slot
from constraints import is_valid_assignment
from cost_function import placement_cost, total_timetable_cost
from heuristic_function import heuristic_function
from search_result import SearchResult


Assignment = Tuple[Course, Slot]


def greedy_best_first_search(
    courses: List[Course],
    slots: List[Slot]
) -> SearchResult:
    """
    Greedy Best-First Search.

    It selects the state with the smallest h(n).
    Unlike A*, it does not include the accumulated cost g(n)
    in its priority calculation.
    """
    start_time = time.perf_counter()
    counter = itertools.count()

    start_state = tuple()
    start_h = heuristic_function(courses, [], slots)
    priority_queue = [(start_h, next(counter), start_state)]

    visited = set()
    nodes_expanded = 0
    nodes_generated = 1

    while priority_queue:
        h_value, _, state = heapq.heappop(priority_queue)

        if state in visited:
            continue

        visited.add(state)

        timetable = [
            (courses[course_index], slots[slot_index])
            for course_index, slot_index in state
        ]

        assigned_indices = {course_index for course_index, _ in state}
        remaining_indices = [
            i for i in range(len(courses)) if i not in assigned_indices
        ]

        if not remaining_indices:
            return SearchResult(
                algorithm="Greedy Best-First Search",
                timetable=timetable,
                total_cost=total_timetable_cost(timetable),
                execution_time=time.perf_counter() - start_time,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                success=True
            )

        nodes_expanded += 1

        next_course_index = remaining_indices[0]
        course = courses[next_course_index]

        for slot_index, slot in enumerate(slots):
            if not is_valid_assignment(course, slot, timetable):
                continue

            new_timetable = timetable + [(course, slot)]
            new_state = state + ((next_course_index, slot_index),)

            if new_state in visited:
                continue

            remaining_courses = [
                courses[i]
                for i in remaining_indices
                if i != next_course_index
            ]

            new_h = heuristic_function(
                remaining_courses, new_timetable, slots
            )

            if new_h == float("inf"):
                continue

            heapq.heappush(
                priority_queue,
                (new_h, next(counter), new_state)
            )
            nodes_generated += 1

    return SearchResult(
        algorithm="Greedy Best-First Search",
        timetable=None,
        total_cost=float("inf"),
        execution_time=time.perf_counter() - start_time,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        success=False
    )
