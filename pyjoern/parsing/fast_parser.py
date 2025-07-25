from pathlib import Path
import importlib.resources
import subprocess
import json
import re

import networkx as nx

from .. import JOERN_SERVER_PATH
from .function import Function

SCALA_SCRIPT_PATH = Path(Path(str(importlib.resources.files("pyjoern"))) / "scala").absolute()
FAST_PARSER_SCRIPT = SCALA_SCRIPT_PATH / "FastParser.sc"
START_DELIM = "PYJOERN_DATA_START\n"
END_DELIM = "PYJOERN_DATA_END\n"


def _run_fast_parser_scala_script(
    source_path: Path,
    no_metadata: bool = False,
    no_cfg: bool = False,
    no_ddg: bool = False,
    no_ast: bool = False,
) -> list[dict]:
    if not JOERN_SERVER_PATH.exists():
        raise FileNotFoundError(f"Joern server binary not found at {JOERN_SERVER_PATH}")
    if not FAST_PARSER_SCRIPT.exists():
        raise FileNotFoundError(f"Fast parser script not found at {FAST_PARSER_SCRIPT}")

    cmd = [
        str(JOERN_SERVER_PATH),
        "--script",
        str(FAST_PARSER_SCRIPT),
        "--param",
        f'target_dir={source_path}'
    ]
    if no_metadata:
        cmd.append("--param")
        cmd.append("no_metadata=true")
    if no_cfg:
        cmd.append("--param")
        cmd.append("no_cfg=true")
    if no_ddg:
        cmd.append("--param")
        cmd.append("no_ddg=true")
    if no_ast:
        cmd.append("--param")
        cmd.append("no_ast=true")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(f"Fast parser failed in script call. Stderr: {proc.stderr} | Stdout: {proc.stdout}")

    parsed_data = []
    found_jsons = re.findall(f"{START_DELIM}(.*?){END_DELIM}", proc.stdout, flags=re.DOTALL)
    for json_str in found_jsons:
        try:
            parsed_data.append(json.loads(json_str))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Fast parser script made non-json compliant output: {json_str[:30]}...")

    return parsed_data


def preprocess_decompilation(decompiled_code_path: Path) -> tuple[bool, bool]:
    # TODO: right now this writes back to file, but all things should be done on a new temp file, fix later
    code_updated = False
    with open(decompiled_code_path, "r") as f:
        code = f.read()

    # check for gotos
    has_gotos = "goto" in code

    # remove special __rustcall in ghidra
    if "__rustcall" in code:
        pattern = r"undefined\s+\[\d{1,4}\]\s+__rustcall"
        code = re.sub(pattern, "undefined", code)
        code_updated |= True

    # remove special ida things
    # TODO: if we ever do more than x64, this needs to be updated!
    replacement_map = {
        "__int8": "char",
        "__int16": "short",
        "__int32": "int",
        "__int64": "long",
        "__fastcall": "",
        "__noreturn": "",
        "__cdecl": "",
    }
    for k, v in replacement_map.items():
        if k in code:
            code = code.replace(k, v)
            code_updated |= True

    # remove things that cause joern to crash
    bad_strings = ["__rustcall",]
    for bad_string in bad_strings:
        if bad_string in code:
            code_updated |= True

        code = code.replace(bad_string, "")

    # header replacements for joern (happens in Rust/C++ decompilation)
    code_lines = code.split("\n")
    header_replacements = {
        "new": "new_joern_token",
        "delete": "delete_joern_token",
    }
    for idx, line in enumerate(code_lines):
        # only for the header!
        if idx > 2:
            break

        # replace if found
        for old, new in header_replacements.items():
            if old in line:
                code_lines[idx] = line.replace(old, new)
                code_updated |= True
    code = "\n".join(code_lines)

    # write back if updated
    if code_updated:
        with open(decompiled_code_path, "w") as f:
            f.write(code)

    return code_updated, has_gotos


def parse_source(
    source_path: Path,
    no_metadata: bool = False,
    no_cfg: bool = False,
    no_ddg: bool = False,
    no_ast: bool = False,
    is_decompilation: bool = False,
) -> dict[str, Function] | dict[tuple[str, str], Function]:
    source_path = Path(source_path).absolute()
    if not source_path.exists():
        raise FileNotFoundError(f"Source file {source_path} does not exist!")

    if is_decompilation:
        preprocess_decompilation(source_path)

    data_dict = _run_fast_parser_scala_script(
        source_path, no_metadata=no_metadata, no_cfg=no_cfg, no_ddg=no_ddg, no_ast=no_ast
    )
    functions_by_name = Function.from_many(data_dict, ignore_cfg=no_cfg)
    if not source_path.is_dir():
        # remove file name from dict since they are all the same
        functions_by_name = {
            k[0]: v for k, v in functions_by_name.items()
        }

    return functions_by_name

def parse_callgraph(source_path: Path, is_decompilation: bool = False) -> nx.DiGraph:
    """
    Given a path to a source file or directory root, parses all functions and creates a callgraph.
    A callgraph is defined as the following:
    - Every node is a function in the source code.
    - Every edge is a call from one function to another.
    - Every node will only appear once in the graph, even if it is called multiple times.

    :param source_path: Path to source file or directory root.
    :param is_decompilation: True when the source is a decompiler created, False otherwise.
    :return:
    """
    # parse the source to get functions
    functions_by_name = parse_source(source_path, no_metadata=True, no_cfg=True, no_ddg=True, no_ast=True, is_decompilation=is_decompilation)

    # create a callgraph
    callgraph = nx.DiGraph()
    edges = []
    for func in functions_by_name.values():
        for callee in func.callees:
            edges.append((func.name, callee))
    callgraph.add_edges_from(edges)

    return callgraph