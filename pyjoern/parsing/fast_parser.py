from pathlib import Path
import importlib.resources
import subprocess
import json
import re

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


def parse_source(
    source_path: Path,
    no_metadata: bool = False,
    no_cfg: bool = False,
    no_ddg: bool = False,
    no_ast: bool = False,
) -> dict[str, Function] | dict[tuple[str, str], Function]:
    source_path = Path(source_path).absolute()
    if not source_path.exists():
        raise FileNotFoundError(f"Source file {source_path} does not exist!")

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
