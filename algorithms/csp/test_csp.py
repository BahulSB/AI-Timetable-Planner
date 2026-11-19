from backtracking import solve as backtracking_solve
from forward_checking import solve as forward_checking_solve

# Small self-contained example. Replace this with the team's actual problem_data
# when integrating with data.py.
sample = {
    "timeslots": [{"id": "T1"}, {"id": "T2"}, {"id": "T3"}],
    "rooms": [{"id": "R1", "capacity": 60}, {"id": "R2", "capacity": 60}],
    "faculty": [{"id": "F1", "unavailable_timeslots": []},
                {"id": "F2", "unavailable_timeslots": []}],
    "courses": [
        {"id": "C1", "faculty_id": "F1", "student_group_id": "G1", "sessions_per_week": 2},
        {"id": "C2", "faculty_id": "F2", "student_group_id": "G2", "sessions_per_week": 2},
    ],
}

if __name__ == "__main__":
    for solver in (backtracking_solve, forward_checking_solve):
        result = solver(sample, timeout_sec=5)
        print(result["algorithm"])
        print("Success:", result["success"])
        print("Schedule entries:", len(result["schedule"]))
        print("Metrics:", result["metrics"])
        assert result["success"], "Solver failed on the sample problem"
        assert len(result["schedule"]) == 4
        assert result["metrics"]["hard_violations"] == 0
    print("CSP tests passed.")
