from io import StringIO
from typing import Iterable

import pytest

from base import SoccerMatchScoresLoader, SoccerTeamRanker
from main import ToIORankingDumper


class MockRanker(SoccerTeamRanker):
    def __init__(self, *dummy_rankings: str):
        self.dummy_rankings = dummy_rankings

    def clear(self):
        pass

    def load_scores(self, loader: SoccerMatchScoresLoader):
        pass

    def iter_rankings(self) -> Iterable[str]:
        for ranking in self.dummy_rankings:
            yield ranking


class TestToIORankingDumper:
    @pytest.fixture
    def mock_output(self):
        return StringIO()

    @pytest.fixture
    def dumper(self, mock_output):
        return ToIORankingDumper(fileio=mock_output)

    def test_empty(self, dumper, mock_output):
        mock_ranker = MockRanker()
        dumper.dump_rankings(mock_ranker)

        mock_output.seek(0)
        assert mock_output.read() == ""

    def test_not_empty(self, dumper, mock_output):
        mock_ranker = MockRanker("test", "other", "foo", "bar", "baz")
        dumper.dump_rankings(mock_ranker)

        mock_output.seek(0)
        assert mock_output.read() == "test\nother\nfoo\nbar\nbaz\n"
