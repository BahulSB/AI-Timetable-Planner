from dataclasses import dataclass
from typing import List, Optional, Tuple
from data import Course, Slot


@dataclass
class SearchResult:
    algorithm: str
    timetable: Optional[List[Tuple[Course, Slot]]]
    total_cost: float
    execution_time: float
    nodes_expanded: int
    nodes_generated: int
    success: bool
