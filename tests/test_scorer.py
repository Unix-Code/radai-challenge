import pytest

from main import MatchResultMetricScorer
from models import MatchScore, TeamGameScore


class TestMatchResultMetricScorer:
    @pytest.fixture
    def scorer(self):
        return MatchResultMetricScorer()

    def test_score_win(self, scorer):
        assert scorer.score(
            MatchScore(TeamGameScore(team_name="a", score=3), TeamGameScore(team_name="b", score=1))
        ) == (3, 0)

    def test_score_loss(self, scorer):
        assert scorer.score(
            MatchScore(
                TeamGameScore(team_name="a", score=2), TeamGameScore(team_name="b", score=10)
            )
        ) == (0, 3)

    def test_score_tie(self, scorer):
        assert scorer.score(
            MatchScore(TeamGameScore(team_name="a", score=3), TeamGameScore(team_name="b", score=3))
        ) == (1, 1)

    def test_sort_order(self, scorer):
        assert scorer.sort_order() == -1

    def test_default(self, scorer):
        assert scorer.default() == 0

    def test_readable_string_from_metric_greater_than_one(self, scorer):
        assert scorer.readable_string_from_metric(3) == "3 pts"

    def test_readable_string_from_metric_equal_to_one(self, scorer):
        assert scorer.readable_string_from_metric(1) == "1 pt"

    def test_readable_string_from_metric_equal_to_zero(self, scorer):
        assert scorer.readable_string_from_metric(0) == "0 pts"
