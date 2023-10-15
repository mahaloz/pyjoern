import sys
import unittest
from pathlib import Path

from pyjoern import fast_cfgs_from_source

TEST_SOURCE_DIR = Path(__file__).absolute().parent / "source"


class TestCFGLifting(unittest.TestCase):
    def test_cfg_structure(self):
        cfg = fast_cfgs_from_source(TEST_SOURCE_DIR / "simple.c")["main"]
        assert cfg is not None


if __name__ == "__main__":
    unittest.main(argv=sys.argv)
