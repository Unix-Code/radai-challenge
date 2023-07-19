from io import StringIO

import pytest

from main import FromIOSoccerMatchScoresLoader
from models import MatchScore, TeamGameScore


class TestFromIOSoccerMatchScoresLoader:
    @pytest.fixture
    def mock_input(self):
        return StringIO()

    @pytest.fixture
    def loader(self, mock_input):
        return FromIOSoccerMatchScoresLoader(fileio=mock_input)

    def test_iter_match_scores_empty(self, loader, mock_input):
        mock_input.write("\n")  # Equivalent to CTRL+D in STDIN
        assert list(loader.iter_match_scores()) == []

    def test_iter_match_scores_valid(self, loader, mock_input):
        mock_input.write(
            "Foo 1, Bar 1\nName With Spaces 1, Numb3r Nam3 0\nSpecialCh@r 6, Numb3r Nam3 1"
        )
        mock_input.seek(0)

        assert list(loader.iter_match_scores()) == [
            MatchScore(
                TeamGameScore(team_name="Foo", score=1), TeamGameScore(team_name="Bar", score=1)
            ),
            MatchScore(
                TeamGameScore(team_name="Name With Spaces", score=1),
                TeamGameScore(team_name="Numb3r Nam3", score=0),
            ),
            MatchScore(
                TeamGameScore(team_name="SpecialCh@r", score=6),
                TeamGameScore(team_name="Numb3r Nam3", score=1),
            ),
        ]

    @pytest.mark.parametrize(
        "invalid_match_score",
        (
            "  InvalidWithLeadingSpace 1, Bar 1",
            "SpecialCh@r 6, InvalidWithTrailingSpace   1",
            "Something totally wrong",
            "Foo -1, Bar 1",
            "Bar 0, Baz -1",
        ),
    )
    def test_iter_match_scores_invalid_match_score_to_parse(
        self, loader, mock_input, invalid_match_score
    ):
        mock_input.write(f"Foo 20, Bar 5\n{invalid_match_score}")
        mock_input.seek(0)

        iterator = iter(loader.iter_match_scores())
        valid_match_score = next(iterator)

        # Assert that subsequent invalid entry is treated as invalid
        with pytest.raises(ValueError, match="Invalid Match Score found in input"):
            next(iterator)

        # Double-check that that's all there is
        with pytest.raises(StopIteration):
            next(iterator)

        assert valid_match_score == MatchScore(
            TeamGameScore(team_name="Foo", score=20), TeamGameScore(team_name="Bar", score=5)
        )

    def test_iter_match_scores_invalid_match_score_team_names(self, loader, mock_input):
        mock_input.write(f"Foo 20, Bar 5\nBaz 1, Baz 2")
        mock_input.seek(0)

        iterator = iter(loader.iter_match_scores())
        valid_match_score = next(iterator)

        # Assert that subsequent invalid entry is treated as invalid
        with pytest.raises(
            ValueError, match="A valid match must contain mutually exclusive team scores"
        ):
            next(iterator)

        # Double-check that that's all there is
        with pytest.raises(StopIteration):
            next(iterator)

        assert valid_match_score == MatchScore(
            TeamGameScore(team_name="Foo", score=20), TeamGameScore(team_name="Bar", score=5)
        )
