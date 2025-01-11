from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import run
import logging

import networkx as nx
import pygraphviz as pg
from cfgutils.transformations import to_supergraph

from .jil.lifter import lift_graph
from .jil.block import Block
from .jil.statement import Nop
from .. import JOERN_PARSE_PATH, JOERN_EXPORT_PATH
from ..utils import WorkDirContext

_l = logging.getLogger(__name__)


def fast_cfgs_from_source(filepath: Path, lift_cfgs=True, supergraph=True, timeout=120):
    filepath = Path(filepath).absolute()
    cfgs = {}
    with TemporaryDirectory() as tmpdir:
        with WorkDirContext(tmpdir):
            # run joern-parser which will output a cpg in the same dir by the
            # filename of "cpg.bin"
            ret = run(f"{JOERN_PARSE_PATH} {filepath}".split(), capture_output=True, timeout=timeout)
            if ret.returncode != 0:
                _l.warning("Joern parse failed, stopping CFG extraction")
                return None

            # extras the cfgs into out_dir in same directory
            ret = run(f"{JOERN_EXPORT_PATH} --repr cfg --out out_dir".split(), capture_output=True, timeout=timeout)
            if ret.returncode != 0:
                _l.warning("Joern Export failed, stopping CFG extraction")
                return None

            out_dir = Path("./out_dir")
            cfg_files = list(out_dir.rglob("*.dot"))
            for cfg_file in cfg_files:
                cfg = cfg_from_dotfile(cfg_file.absolute())
                if not cfg or not len(cfg.nodes):
                    continue

                if cfg.name in cfgs and len(cfg.nodes) < len(cfgs[cfg.name].nodes):
                    continue

                cfgs[cfg.name] = nx.DiGraph(cfg)

    normalized_cfgs = {}
    for cfg_name, cfg in cfgs.items():
        normalized_cfgs[cfg_name] = normalize_cfg(cfg, lift_cfg=lift_cfgs, supergraph=supergraph)

    return normalized_cfgs


def normalize_cfg(cfg: nx.DiGraph, lift_cfg=True, supergraph=True, remove_singleton_funcend=True):
    if lift_cfg:
        jil_cfg = lift_graph(cfg)
        jil_cfg.name = cfg.name
        jil_cfg = to_supergraph(jil_cfg) if supergraph else jil_cfg
        cfg = jil_cfg

    node_attrs = {}
    edge_attrs = {}
    for node in cfg.nodes:
        node_attrs[node] = {'node': node}
    for edgd in cfg.edges:
        edge_attrs[edgd] = {'src': edgd[0], 'dst': edgd[1]}

    nx.set_node_attributes(cfg, node_attrs)
    nx.set_edge_attributes(cfg, edge_attrs)

    # When joern creates a CFG, it uses special nodes, called funcends here, to represent the end of a function.
    # This can be seen if you have a program with multiple returns. Each return node will have an edge to the
    # funcend node. This is normally fine, but, when you use metrics on a CFG that rely on the number of edges
    # and nodes in the CFG, the funcend node can skew the results. The flag below for this specific case, since
    # there can be funcend nodes that get merged with normal code, or programs that have many in them.
    if remove_singleton_funcend:
        # find the singleton funcend node and remove it (but only if there is only one)
        funcends = []
        for node in cfg.nodes:
            node: Block
            if cfg.out_degree(node) == 0 and len(node.statements) == 1:
                stmt = node.statements[0]
                if isinstance(stmt, Nop) and stmt.type == Nop.FUNC_END:
                    funcends.append(node)

        if len(funcends) == 1:
            cfg.remove_node(funcends[0])

    return cfg


def parse_dot_cfg_string(dotcfg_string):
    try:
        graph = nx.nx_agraph.from_agraph(pg.AGraph(dotcfg_string))
    except Exception as e:
        _l.critical(f"Failed to parse CFG from dot string: {e}")
        graph = None

    return graph


def cfg_from_dotfile(filepath: Path):
    filepath = Path(filepath).expanduser().absolute()
    with open(filepath, "r") as fp:
        data = fp.read()

    return parse_dot_cfg_string(data)
