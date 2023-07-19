from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class TeamGameScore:
    team_name: str
    score: int

    def __post_init__(self):
        # Performing this validation using the stdlib, but this can be done using a separate
        # serialization/validation library like Marshmallow or Pydantic or attrs
        if not self.team_name:
            raise ValueError("Name must be not empty")
        elif self.score < 0:
            raise ValueError("Score must be >= 0")


@dataclass(frozen=True)
class MatchScore:
    team_score_a: TeamGameScore
    team_score_b: TeamGameScore

    def __post_init__(self):
        # Performing this validation using the stdlib, but this can be done using a separate
        # serialization/validation library like Marshmallow or Pydantic or attrs
        if self.team_score_a.team_name == self.team_score_b.team_name:
            raise ValueError("A valid match must contain mutually exclusive team scores")


class SoccerMatchResult(Enum):
    WIN = "WIN"
    TIE = "TIE"
    LOSS = "LOSS"
