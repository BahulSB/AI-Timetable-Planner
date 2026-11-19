from typing import List, Tuple
from data import Course, Slot
from constraints import is_valid_assignment
from cost_function import total_timetable_cost
from search_result import SearchResult


Assignment = Tuple[Course, Slot]


def count_hard_constraint_violations(
    timetable: List[Assignment]
) -> int:
    """Count pairwise hard-constraint violations in a completed timetable."""
    violations = 0

    for i in range(len(timetable)):
        course1, slot1 = timetable[i]

        for j in range(i + 1, len(timetable)):
            course2, slot2 = timetable[j]

            same_time = (
                slot1.day == slot2.day
                and slot1.period == slot2.period
            )

            if not same_time:
                continue

            if course1.faculty == course2.faculty:
                violations += 1
            if course1.student_group == course2.student_group:
                violations += 1
            if slot1.room == slot2.room:
                violations += 1

    return violations


def count_preference_violations(
    timetable: List[Assignment]
) -> int:
    return sum(
        (slot.day, slot.period) not in course.preferred_slots
        for course, slot in timetable
    )


def count_student_gaps(
    timetable: List[Assignment]
) -> int:
    """Count empty periods between classes of the same group on the same day."""
    gaps = 0

    for i in range(len(timetable)):
        course1, slot1 = timetable[i]

        for j in range(i + 1, len(timetable)):
            course2, slot2 = timetable[j]

            if (
                course1.student_group == course2.student_group
                and slot1.day == slot2.day
            ):
                gap = abs(slot1.period - slot2.period) - 1
                if gap > 0:
                    gaps += gap

    return gaps


def display_timetable(timetable: List[Assignment]) -> None:
    if timetable is None:
        print("No valid timetable was found.")
        return

    print(
        f"{'Subject':<25} {'Faculty':<12} {'Group':<10} "
        f"{'Day':<12} {'Period':<8} {'Room':<10}"
    )
    print("-" * 85)

    ordered = sorted(
        timetable,
        key=lambda item: (item[1].day, item[1].period, item[1].room)
    )

    for course, slot in ordered:
        print(
            f"{course.name:<25} {course.faculty:<12} "
            f"{course.student_group:<10} {slot.day:<12} "
            f"{slot.period:<8} {slot.room:<10}"
        )


def display_comparison(results: List[SearchResult]) -> None:
    print("\nALGORITHM PERFORMANCE COMPARISON")
    print("-" * 105)
    print(
        f"{'Algorithm':<28} {'Success':<10} {'Cost':<10} "
        f"{'Time (s)':<13} {'Expanded':<12} {'Generated':<12}"
    )
    print("-" * 105)

    for result in results:
        cost = result.total_cost if result.success else "N/A"
        print(
            f"{result.algorithm:<28} {str(result.success):<10} "
            f"{str(cost):<10} {result.execution_time:<13.6f} "
            f"{result.nodes_expanded:<12} {result.nodes_generated:<12}"
        )

        if result.success:
            print(
                "  Hard violations:",
                count_hard_constraint_violations(result.timetable),
                "| Preference violations:",
                count_preference_violations(result.timetable),
                "| Student gaps:",
                count_student_gaps(result.timetable)
            )
