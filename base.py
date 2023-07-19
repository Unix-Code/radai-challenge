from abc import abstractmethod
from typing import Iterable, Literal, Protocol

from models import MatchScore


class SoccerMatchScoresLoader(Protocol):
    @abstractmethod
    def iter_match_scores(self) -> Iterable[MatchScore]:
        ...


class MetricScorer(Protocol):
    @abstractmethod
    def readable_string_from_metric(self, metric: int) -> str:
        """Returns human-readable string given metric value"""
        ...

    @abstractmethod
    def default(self) -> int:
        """Returns default metric value"""
        ...

    @abstractmethod
    def sort_order(self) -> Literal[-1, 1]:
        """
        Sort order (-1 for descending, 1 for ascending)
        """
        ...

    @abstractmethod
    def score(self, match_score: MatchScore) -> tuple[int, int]:
        """
        Returns a pair of integer scoring metrics that can be used to compare a pair of teams
        over a set of match score results.
        """
        ...


class SoccerTeamRanker(Protocol):
    @abstractmethod
    def clear(self):
        ...

    @abstractmethod
    def load_scores(self, loader: SoccerMatchScoresLoader):
        ...

    @abstractmethod
    def iter_rankings(self) -> Iterable[str]:
        ...


class RankingDumper(Protocol):
    @abstractmethod
    def dump_rankings(self, ranker: SoccerTeamRanker):
        ...
