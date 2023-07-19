from typing import Iterable

from base import SoccerMatchScoresLoader
from main import MatchResultMetricScorer, StandardCompetitionSoccerTeamRanker
from models import MatchScore, TeamGameScore


class MockScoreLoader(SoccerMatchScoresLoader):
    def __init__(self, *dummy_scores):
        self.dummy_scores = dummy_scores

    def iter_match_scores(self) -> Iterable[MatchScore]:
        for score in self.dummy_scores:
            yield score


class TestStandardCompetitionSoccerTeamRanker:
    def test_no_scorers(self):
        """
        GIVEN no metric scorers
        RESULT should be derived only from team name alphabetical sort
          and no metrics should be shown
        """
        mock_score_loader = MockScoreLoader(
            MatchScore(
                TeamGameScore(team_name="a", score=1), TeamGameScore(team_name="b", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="b", score=2), TeamGameScore(team_name="c", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="a", score=25), TeamGameScore(team_name="d", score=0)
            ),
            MatchScore(
                TeamGameScore(team_name="b", score=76), TeamGameScore(team_name="d", score=2)
            ),
        )
        ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[])
        ranker.load_scores(mock_score_loader)

        expected_rankings = ["1. a", "2. b", "3. c", "4. d"]
        assert list(ranker.iter_rankings()) == expected_rankings

    def test_no_scores(self):
        """
        GIVEN no match scores
        RESULT should be empty
        """
        mock_score_loader = MockScoreLoader()
        ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[MatchResultMetricScorer()])
        ranker.load_scores(mock_score_loader)
        assert list(ranker.iter_rankings()) == []

    def test_in_order_by_match_result(self):
        """
        GIVEN MatchResultMetricScorer
        RESULT should be derived only from team name alphabetical sort
          and no metrics should be shown
        """
        mock_score_loader = MockScoreLoader(
            MatchScore(
                TeamGameScore(team_name="a", score=1), TeamGameScore(team_name="b", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="b", score=2), TeamGameScore(team_name="c", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="a", score=25), TeamGameScore(team_name="d", score=0)
            ),
            MatchScore(
                TeamGameScore(team_name="b", score=76), TeamGameScore(team_name="d", score=2)
            ),
        )
        ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[MatchResultMetricScorer()])
        ranker.load_scores(mock_score_loader)

        expected_rankings = ["1. b, 7 pts", "2. a, 4 pts", "3. c, 0 pts", "3. d, 0 pts"]
        assert list(ranker.iter_rankings()) == expected_rankings

    def test_in_order_by_match_result_long_tie(self):
        mock_score_loader = MockScoreLoader(
            MatchScore(
                TeamGameScore(team_name="a", score=1), TeamGameScore(team_name="b", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="c", score=1), TeamGameScore(team_name="d", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="e", score=1), TeamGameScore(team_name="f", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="g", score=1), TeamGameScore(team_name="h", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="i", score=1), TeamGameScore(team_name="j", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="k", score=1), TeamGameScore(team_name="l", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="m", score=1), TeamGameScore(team_name="n", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="o", score=1), TeamGameScore(team_name="p", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="q", score=1), TeamGameScore(team_name="r", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="t", score=1), TeamGameScore(team_name="u", score=0)
            ),
        )
        ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[MatchResultMetricScorer()])
        ranker.load_scores(mock_score_loader)

        expected_rankings = [
            "1. t, 3 pts",
            "2. a, 1 pt",
            "2. b, 1 pt",
            "2. c, 1 pt",
            "2. d, 1 pt",
            "2. e, 1 pt",
            "2. f, 1 pt",
            "2. g, 1 pt",
            "2. h, 1 pt",
            "2. i, 1 pt",
            "2. j, 1 pt",
            "2. k, 1 pt",
            "2. l, 1 pt",
            "2. m, 1 pt",
            "2. n, 1 pt",
            "2. o, 1 pt",
            "2. p, 1 pt",
            "2. q, 1 pt",
            "2. r, 1 pt",
            "20. u, 0 pts",
        ]
        assert list(ranker.iter_rankings()) == expected_rankings

    def test_in_order_by_match_result_multiple_ties(self):
        mock_score_loader = MockScoreLoader(
            MatchScore(
                TeamGameScore(team_name="a", score=2), TeamGameScore(team_name="b", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="x", score=2), TeamGameScore(team_name="b", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="b", score=0), TeamGameScore(team_name="a", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="c", score=1), TeamGameScore(team_name="d", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="d", score=1), TeamGameScore(team_name="c", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="c", score=1), TeamGameScore(team_name="d", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="e", score=1), TeamGameScore(team_name="f", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="f", score=1), TeamGameScore(team_name="e", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="g", score=1), TeamGameScore(team_name="h", score=1)
            ),
        )
        ranker = StandardCompetitionSoccerTeamRanker(metric_scorers=[MatchResultMetricScorer()])
        ranker.load_scores(mock_score_loader)

        expected_rankings = [
            "1. a, 6 pts",
            "2. c, 3 pts",
            "2. d, 3 pts",
            "2. x, 3 pts",
            "5. e, 2 pts",
            "5. f, 2 pts",
            "7. g, 1 pt",
            "7. h, 1 pt",
            "9. b, 0 pts",
        ]
        assert list(ranker.iter_rankings()) == expected_rankings
