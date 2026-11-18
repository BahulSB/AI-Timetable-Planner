# Member 2 - Heuristic Search and Optimization

This folder contains the A* Search and Greedy Best-First Search implementation
for the College Timetable Planner.

## Files

- `data.py` - sample courses, rooms, periods and time slots
- `constraints.py` - hard-constraint checking
- `cost_function.py` - soft-constraint penalty calculation
- `heuristic_function.py` - estimated remaining scheduling cost
- `astar.py` - A* search implementation
- `greedy_best_first.py` - Greedy Best-First Search implementation
- `search_result.py` - common result structure
- `evaluation.py` - timetable display and performance metrics
- `main.py` - program entry point

## Requirements

Python 3.8 or later. No external packages are required.

## Run

Open a terminal inside this folder and run:

```bash
python main.py
```

## Soft constraints

The current cost function includes:
1. Faculty preferred time slots
2. First-period inconvenience
3. Last-period inconvenience
4. Gaps between classes of the same student group

Lower total cost indicates a better schedule.

## Hard constraints

The current implementation checks:
1. Faculty clashes
2. Student-group clashes
3. Room clashes

## Important integration note

The sample dataset is for standalone testing. During integration, replace
`create_sample_courses()` and `create_slots()` with the actual data supplied
by the team's CSP/data module. Keep the `Course` and `Slot` fields consistent,
or write a small adapter to convert the team's data into these structures.

The current model schedules one meeting per course. If the project requires
multiple weekly meetings per course, extend the course/session representation
before using this implementation for the final experiment.
