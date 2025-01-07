import sys
import unittest
from pathlib import Path

from pyjoern import fast_cfgs_from_source, parse_source, JoernClient, JoernServer
from pyjoern.parsing.function import Function

TEST_SOURCE_DIR = Path(__file__).absolute().parent / "source"


class TestParsing(unittest.TestCase):
    def test_single_file_parser(self):
        functions = parse_source(TEST_SOURCE_DIR / "simple.c")
        assert len(functions) == 2

        schedule_job = functions.get("schedule_job", None)
        assert schedule_job is not None
        assert schedule_job.name == "schedule_job"
        assert schedule_job.start_line == 1
        assert schedule_job.end_line == 19
        assert len(schedule_job.gotos) == 1
        assert schedule_job.cfg is not None
        assert schedule_job.ddg is not None

        # manually counted
        assert len(schedule_job.ast.nodes) == 32

    def test_multiple_file_parser(self):
        functions = parse_source(TEST_SOURCE_DIR / "nginx")

        func1: Function = functions.get(('ngx_mail_pop3_init_session', 'fake_handler.c'), None)
        assert func1 is not None
        # make sure this is the definition not the declaration
        assert func1.start_line == 6

        func2: Function = functions.get(('ngx_mail_pop3_init_session', 'ngx_mail_pop3_handler.c'), None)
        assert func2 is not None

        assert len(functions) == 11

    def test_decompiler_c_parser(self):
        functions = parse_source(TEST_SOURCE_DIR / "ida9_fmt_coreutils.c")
        assert len(functions) == 23

    def test_parsing_disabling(self):
        funcs = parse_source(TEST_SOURCE_DIR / "simple.c", no_metadata=True)
        assert funcs['schedule_job'].filename is not None
        assert not funcs['schedule_job'].control_structures

        funcs = parse_source(TEST_SOURCE_DIR / "simple.c", no_metadata=True, no_cfg=True)
        assert not funcs['schedule_job'].cfg

        funcs = parse_source(TEST_SOURCE_DIR / "simple.c", no_metadata=True, no_cfg=True, no_ddg=True)
        assert not funcs['schedule_job'].ddg

        funcs = parse_source(TEST_SOURCE_DIR / "simple.c", no_metadata=True, no_cfg=True, no_ddg=True, no_ast=True)
        assert not funcs['schedule_job'].ast

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
