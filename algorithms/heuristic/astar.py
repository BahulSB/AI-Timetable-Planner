import heapq
import itertools
import time
from typing import List, Tuple

from data import Course, Slot
from constraints import is_valid_assignment
from cost_function import placement_cost
from heuristic_function import heuristic_function
from search_result import SearchResult


Assignment = Tuple[Course, Slot]


def a_star_search(
    courses: List[Course],
    slots: List[Slot]
) -> SearchResult:
    """
    A* search using f(n) = g(n) + h(n).

    g(n): penalty accumulated so far.
    h(n): estimated minimum additional penalty.
    """
    start_time = time.perf_counter()
    counter = itertools.count()

    # Each state is a tuple of (course_index, slot_index) assignments.
    start_state = tuple()

    start_h = heuristic_function(courses, [], slots)
    priority_queue = [(start_h, 0, next(counter), start_state)]

    best_cost = {start_state: 0}
    nodes_expanded = 0
    nodes_generated = 1

    while priority_queue:
        f_value, current_cost, _, state = heapq.heappop(priority_queue)

        # Ignore an outdated queue entry.
        if current_cost != best_cost.get(state):
            continue

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
                algorithm="A* Search",
                timetable=timetable,
                total_cost=current_cost,
                execution_time=time.perf_counter() - start_time,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                success=True
            )

        nodes_expanded += 1

        # Fixed course order keeps the state space easy to understand
        # and ensures each partial assignment has one construction order.
        next_course_index = remaining_indices[0]
        course = courses[next_course_index]

        for slot_index, slot in enumerate(slots):
            if not is_valid_assignment(course, slot, timetable):
                continue

            step_cost = placement_cost(course, slot, timetable)
            new_cost = current_cost + step_cost
            new_state = state + ((next_course_index, slot_index),)

            if new_cost >= best_cost.get(new_state, float("inf")):
                continue

            new_timetable = timetable + [(course, slot)]
            remaining_courses = [
                courses[i]
                for i in remaining_indices
                if i != next_course_index
            ]

            h_value = heuristic_function(
                remaining_courses, new_timetable, slots
            )

            if h_value == float("inf"):
                continue

            best_cost[new_state] = new_cost
            heapq.heappush(
                priority_queue,
                (
                    new_cost + h_value,
                    new_cost,
                    next(counter),
                    new_state
                )
            )
            nodes_generated += 1

    return SearchResult(
        algorithm="A* Search",
        timetable=None,
        total_cost=float("inf"),
        execution_time=time.perf_counter() - start_time,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        success=False
    )
