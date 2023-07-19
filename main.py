import re
import sys
from collections import defaultdict
from contextlib import nullcontext
from pathlib import Path
from sys import stdin, stdout
from typing import Iterable, Literal, TextIO, cast

from base import MetricScorer, RankingDumper, SoccerMatchScoresLoader, SoccerTeamRanker
from models import MatchScore, SoccerMatchResult, TeamGameScore


class FromIOSoccerMatchScoresLoader(SoccerMatchScoresLoader):
    # Something akin to:
    # Team N@m3 12345, Other T3am Name 5
    MATCH_SCORE_PATTERN = re.compile(
        r"(?P<team_name_a>\S{1}(?:.*\S{1})?) (?P<team_score_a>\d+), "
        r"(?P<team_name_b>\S{1}(?:.*\S{1})?) (?P<team_score_b>\d+)"
    )

    def __init__(self, fileio: TextIO):
        self.fileio = fileio

    def iter_match_scores(self) -> Iterable[MatchScore]:
        while not self.fileio.closed:
            raw_match_score = self.fileio.readline()
            if not raw_match_score:
                break
            regex_match = re.match(self.MATCH_SCORE_PATTERN, raw_match_score)
            if regex_match is None or len(regex_match.groups()) != 4:
                # Handling this as a loud error to avoid returning a ranking with invalid input
                raise ValueError("Invalid Match Score found in input")
            team_name_a, team_score_a, team_name_b, team_score_b = regex_match.groups()
            yield MatchScore(
                TeamGameScore(team_name_a, int(team_score_a)),
                TeamGameScore(team_name_b, int(team_score_b)),
            )


class MatchResultMetricScorer(MetricScorer):
    POINTS_BY_RESULT = {
        SoccerMatchResult.WIN: 3,
        SoccerMatchResult.TIE: 1,
        SoccerMatchResult.LOSS: 0,
    }

    def readable_string_from_metric(self, metric: int) -> str:
        unit_str = "pt" if metric == 1 else "pts"
        return f"{metric} {unit_str}"

    def default(self) -> int:
        return 0

    def sort_order(self) -> Literal[-1, 1]:
        return -1

    def score(self, match_score: MatchScore) -> tuple[int, int]:
        if match_score.team_score_a.score > match_score.team_score_b.score:
            match_result_for_team_a = SoccerMatchResult.WIN
            match_result_for_team_b = SoccerMatchResult.LOSS
        elif match_score.team_score_a.score == match_score.team_score_b.score:
            match_result_for_team_a = SoccerMatchResult.TIE
            match_result_for_team_b = SoccerMatchResult.TIE
        else:
            match_result_for_team_a = SoccerMatchResult.LOSS
            match_result_for_team_b = SoccerMatchResult.WIN

        return (
            self.POINTS_BY_RESULT[match_result_for_team_a],
            self.POINTS_BY_RESULT[match_result_for_team_b],
        )


class StandardCompetitionSoccerTeamRanker(SoccerTeamRanker):
    def __init__(self, metric_scorers: list[MetricScorer]):
        self.teams: set[str] = set()
        self.metric_scorers: list[MetricScorer] = metric_scorers
        self.metrics: list[dict[str, int]] = [
            defaultdict(metric_scorer.default) for metric_scorer in metric_scorers
        ]
        # This a list of ranking groups, nested lists are ranked teams within the same ranking group
        # (ie both 3rd place)
        self.rankings: list[list[str]] = []

    def clear(self):
        for metric_lookup in self.metrics:
            metric_lookup.clear()
        self.rankings.clear()
        self.teams.clear()

    def _metric_scorers_and_lookups(self) -> Iterable[tuple[MetricScorer, dict[str, int]]]:
        return zip(self.metric_scorers, self.metrics)

    @property
    def _sort_decorated_teams(self) -> Iterable[tuple[int | str, ...]]:
        """
        Generate decorated items for easy sorting like so: (metric_a, -metric_b, ..., team_name)
        """
        return (
            tuple(
                [
                    *(
                        metric_lookup[team_name] * metric_scorer.sort_order()
                        for metric_scorer, metric_lookup in self._metric_scorers_and_lookups()
                    ),
                    team_name,
                ]
            )
            for team_name in self.teams
        )

    def _generate_rankings(self):
        self.rankings.clear()
        current_rank_group = []
        last_comparable_values = None

        for comparable_values in sorted(self._sort_decorated_teams):
            *metric_values, team_name = comparable_values
            if metric_values:
                # This is for the artificial case where there are no scoring metrics configured.
                # It'd be nice to not show any trailing metric text as well as split each unique
                # team name into a separate ranking group.
                comparable_values = metric_values
            if last_comparable_values is None or comparable_values == last_comparable_values:
                current_rank_group.append(team_name)
            else:
                self.rankings.append(current_rank_group)
                current_rank_group = [team_name]
            last_comparable_values = comparable_values
        if current_rank_group:
            self.rankings.append(current_rank_group)

    def load_scores(self, loader: SoccerMatchScoresLoader):
        for match_score in loader.iter_match_scores():
            self.teams.add(match_score.team_score_a.team_name)
            self.teams.add(match_score.team_score_b.team_name)
            for metric_scorer, metric_lookup in self._metric_scorers_and_lookups():
                metric_a, metric_b = cast(MetricScorer, metric_scorer).score(match_score)
                metric_lookup[match_score.team_score_a.team_name] += metric_a
                metric_lookup[match_score.team_score_b.team_name] += metric_b
        self._generate_rankings()

    def iter_rankings(self) -> Iterable[str]:
        next_ranking = 1
        for ranking_group in self.rankings:
            curr_ranking = next_ranking
            for team_name in ranking_group:
                ranking_text_parts = [f"{curr_ranking}. {team_name}"]
                metrics_text = ", ".join(
                    metric_scorer.readable_string_from_metric(metric_lookup[team_name])
                    for metric_scorer, metric_lookup in self._metric_scorers_and_lookups()
                )
                if metrics_text:
                    ranking_text_parts.append(metrics_text)
                yield ", ".join(ranking_text_parts)
                next_ranking += 1


class ToIORankingDumper(RankingDumper):
    def __init__(self, fileio: TextIO):
        self.fileio = fileio

    def dump_rankings(self, ranker: SoccerTeamRanker):
        for rank_value in ranker.iter_rankings():
            self.fileio.write(rank_value)
            self.fileio.write("\n")
            self.fileio.flush()


def handle_input_args() -> Path | None:
    # Opted to use sys.argv but argparse or click (additional package dependency) would also work
    script_args = sys.argv[1:]
    if len(script_args) > 1:
        sys.exit("Invalid: Only 1 argument consisting of a file path is allowed.\n")
    elif script_args == ["--help"]:
        print("Usage:\n<file_path> (Input File to use as input)\n<No Args> (Use STDIN as input)\n")
        sys.exit()

    return Path(script_args[0]) if script_args else None


def main(file_path: Path | None):
    ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[MatchResultMetricScorer()])

    with open(file_path, "r") if file_path is not None else nullcontext() as input_fileio:
        io_loader = FromIOSoccerMatchScoresLoader(
            fileio=input_fileio if file_path is not None else stdin
        )
        ranker.load_scores(io_loader)
    io_dumper = ToIORankingDumper(fileio=stdout)
    io_dumper.dump_rankings(ranker)


if __name__ == "__main__":
    main(handle_input_args())
