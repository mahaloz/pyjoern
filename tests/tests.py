import sys
import unittest
from pathlib import Path

from pyjoern import fast_cfgs_from_source, JoernClient, JoernServer

TEST_SOURCE_DIR = Path(__file__).absolute().parent / "source"


class TestFastLifters(unittest.TestCase):
    def test_fast_cfg(self):
        cfg = fast_cfgs_from_source(TEST_SOURCE_DIR / "simple.c")["main"]
        assert cfg is not None


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
