import sys
import unittest
from pathlib import Path

from pyjoern import fast_cfgs_from_source, parse_source, JoernClient, JoernServer

TEST_SOURCE_DIR = Path(__file__).absolute().parent / "source"


class TestParsing(unittest.TestCase):
    def test_parser(self):
        functions = parse_source(TEST_SOURCE_DIR / "simple.c")
        assert len(functions) == 2

        schedule_job = functions.get("schedule_job", None)
        assert schedule_job is not None
        assert schedule_job.name == "schedule_job"
        assert schedule_job.start_line == 1
        assert schedule_job.end_line == 19
        assert len(schedule_job.gotos) == 1
        assert schedule_job.cfg is not None

    def test_fast_cfg(self):
        cfg = fast_cfgs_from_source(TEST_SOURCE_DIR / "simple.c")["main"]
        assert cfg is not None, "CFG did not actually parse"


class TestJoernServer(unittest.TestCase):
    def test_server(self):
        with JoernServer() as server:
            assert server is not None

            client = JoernClient(TEST_SOURCE_DIR / "simple.c", port=server.port)
            assert client is not None

            funcs = client.functions
            assert 'main' in funcs


if __name__ == "__main__":
    unittest.main(argv=sys.argv)
