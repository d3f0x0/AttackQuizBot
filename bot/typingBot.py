from typing import NamedTuple
from typing import Literal


class StaticMitre(NamedTuple):
    tactic: int
    tech: int
    mitigations: int
    all_stat: int


class Quiz(NamedTuple):
    answers: list[str]
    true_answer: Literal[0:int, 1:int, 2:int, 3:int]
    question: str
    mitre_id: str
