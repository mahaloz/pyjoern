from pathlib import Path

import networkx as nx

from ..cfg import parse_dot_cfg_string, normalize_cfg


class Function:
    def __init__(
        self,
        name: str = None,
        return_type: str | None = None,
        calls: list[str] | None = None,
        macro_count: int | None = None,
        control_structures: list[str] | None = None,
        gotos: list[str] | None = None,
        fullname: str | None = None,
        filename: str | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
        signature: str | None = None,
        cfg: nx.DiGraph | str | list | None = None,
    ):
        self.name = name
        self.return_type = return_type
        self.calls = calls or []
        self.macro_count = macro_count or 0
        self.control_structures = control_structures or []
        self.gotos = gotos or []
        self.fullname = fullname
        self.filename: Path | None = Path(filename)
        self.start_line = start_line
        self.end_line = end_line
        self.signature = signature
        self.cfg = self._parse_dot_cfg_string(cfg) if isinstance(cfg, (str, list)) else cfg

    def __str__(self):
        return f"<Function {self.name} {self.signature} {self.start_line}:{self.end_line}>"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def _parse_dot_cfg_string(cfg_data: str | list) -> nx.DiGraph:
        cfg_str = cfg_data if isinstance(cfg_data, str) else cfg_data[0]
        parsed_cfg = parse_dot_cfg_string(cfg_str)
        if parsed_cfg is not None:
            parsed_cfg = normalize_cfg(parsed_cfg, lift_cfg=True, supergraph=True)

        return parsed_cfg

    @staticmethod
    def from_many(data: list[dict]) -> dict[str, "Function"]:
        functions = [Function(**d) for d in data]
        blacklisted_names = [
            "<", "+", "*", "(", ">", "JUMPOUT", "__builtin_unreachable"
        ]
        func_by_name = {}
        for f in functions:
            if not f.name or any(f.name.startswith(bl) for bl in blacklisted_names):
                continue

            cfg = f.cfg
            if not cfg or not len(cfg.nodes):
                continue

            # normalize out some bad funcs
            prev_func = func_by_name.get(f.name, None)
            if prev_func is not None and prev_func.cfg is not None and len(cfg.nodes) < len(prev_func.cfg.nodes):
                continue

            func_by_name[f.name] = f

        return func_by_name
