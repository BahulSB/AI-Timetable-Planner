from data import create_sample_courses, create_slots
from astar import a_star_search
from greedy_best_first import greedy_best_first_search
from evaluation import display_timetable, display_comparison


def main():
    courses = create_sample_courses()
    slots = create_slots()

    print("COLLEGE TIMETABLE PLANNER")
    print("Number of courses:", len(courses))
    print("Number of available slots:", len(slots))

    astar_result = a_star_search(courses, slots)
    greedy_result = greedy_best_first_search(courses, slots)

    results = [astar_result, greedy_result]

    for result in results:
        print("\n" + "=" * 60)
        print(result.algorithm)
        print("=" * 60)

        if result.success:
            display_timetable(result.timetable)
            print("Total soft-constraint cost:", result.total_cost)
        else:
            print("No valid timetable could be generated.")

    display_comparison(results)


if __name__ == "__main__":
    main()
