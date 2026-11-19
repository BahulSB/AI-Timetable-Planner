from dataclasses import dataclass
from typing import FrozenSet, List, Tuple


@dataclass(frozen=True)
class Slot:
    day: str
    period: int
    room: str


@dataclass(frozen=True)
class Course:
    course_id: str
    name: str
    faculty: str
    student_group: str
    preferred_slots: FrozenSet[Tuple[str, int]]


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = [1, 2, 3, 4, 5, 6]
ROOMS = ["Room101", "Room102", "Room103"]


def create_slots() -> List[Slot]:
    """Create every available day-period-room combination."""
    return [
        Slot(day, period, room)
        for day in DAYS
        for period in PERIODS
        for room in ROOMS
    ]


def create_sample_courses() -> List[Course]:
    """Small sample dataset. Replace this with the team's actual input."""
    return [
        Course("C01", "Data Structures", "FacultyA", "CSE-A",
               frozenset({("Monday", 1), ("Wednesday", 2)})),
        Course("C02", "Database Systems", "FacultyB", "CSE-A",
               frozenset({("Monday", 2), ("Tuesday", 2)})),
        Course("C03", "Artificial Intelligence", "FacultyA", "CSE-B",
               frozenset({("Tuesday", 1), ("Thursday", 3)})),
        Course("C04", "Operating Systems", "FacultyC", "CSE-A",
               frozenset({("Wednesday", 3), ("Friday", 2)})),
        Course("C05", "Computer Networks", "FacultyD", "CSE-B",
               frozenset({("Monday", 3), ("Thursday", 2)})),
        Course("C06", "Discrete Mathematics", "FacultyE", "CSE-A",
               frozenset({("Tuesday", 3), ("Friday", 1)})),
    ]
