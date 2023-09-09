from subprocess import run
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import logging
import os
from typing import Dict

import networkx
from networkx import Graph, DiGraph

from ..utils import WorkDirContext
from .jil.lifter import lift_graph
from .jil.block import Block
from .jil.statement import Nop, Statement
from ...utils.binary_debug_info import read_line_maps

import networkx as nx
import pygraphviz as pg
import graphviz

l = logging.getLogger(__name__)


def addr_to_node_map(graph):
    return {
        node.addr: node for node in graph.nodes
    }


def find_function_root_node(graph: nx.DiGraph):
    for node in graph.nodes:
        first_stmt = node.statements[0]
        if isinstance(first_stmt, Nop) and first_stmt.type == Nop.FUNC_START:
            return node

    return None


def correct_decompiler_mappings(dec_cfg, dec_line_to_addr_map):
    node: Block = find_function_root_node(dec_cfg)
    if node is None:
        raise Exception("Could not find root node!")

    base = node.addr - 1
    corrected_line_nums = {k+base: v for k, v in dec_line_to_addr_map.items()}
    line_nums = corrected_line_nums.keys()
    first_ln = min(line_nums)
    last_ln = max(line_nums)

    for ln in range(first_ln, last_ln):
        val = corrected_line_nums.get(ln, None)
        if val is not None:
            continue

        # search for a value expanding pos and negative equally until
        # another line have a value that can be used
        reach = 1
        is_neg = True
        while reach < last_ln:
            curr_reach = 0 - reach if is_neg else reach
            val = corrected_line_nums.get(ln + curr_reach, None)
            # leave when we find a good val
            if val is not None:
                corrected_line_nums[ln] = val
                break

            reach += 1
            is_neg ^= True

    return corrected_line_nums


def correct_source_cfg_addrs(cfgs: Dict[str, nx.DiGraph], line_map_file: Path):
    line_map_file = Path(line_map_file).absolute()
    func_correct_line_map = read_line_maps(line_map_file, value_is_set_type=False)

    new_cfgs = {}
    for cfg_name, cfg in cfgs.items():
        # skip cfgs without mappings
        line_to_correct_map = func_correct_line_map.get(cfg_name, None)
        if line_to_correct_map is None:
            continue

        nodes_map = {}
        new_graph = nx.DiGraph()
        for node in cfg:
            node_copy = node.copy()
            new_addr = line_to_correct_map.get(node.addr, None)
            if new_addr is not None:
                node_copy.addr = new_addr
            else:
                l.warning(f"Parsed a block: {node} without a mapping for lineaddrs!")

            for stmt in node_copy.statements:
                new_addr = line_to_correct_map.get(stmt.source_line_number, None)
                if new_addr is None:
                    l.warning(f"Parsed a block statement: {stmt} without a mapping for lineaddrs!")
                    continue

                stmt.source_line_number = new_addr

            nodes_map[node] = node_copy

        new_graph.add_nodes_from(nodes_map.values())
        for src, dst in cfg.edges:
            new_graph.add_edge(nodes_map[src], nodes_map[dst])

        new_cfgs[cfg_name] = new_graph

    return new_cfgs

def extract_cfgs_from_source(filepath: Path, lift_cfgs=True):
    filepath = Path(filepath).absolute()
    cfgs = {}
    with TemporaryDirectory() as tmpdir:
        with WorkDirContext(tmpdir):
            # run joern-parser which will output a cpg in the same dir by the
            # filename of "cpg.bin"
            ret = run(f"joern-parse {filepath}".split(), capture_output=True)
            if ret.returncode != 0:
                l.warning("Joern parse failed, stopping CFG extraction")
                return None

            # extras the cfgs into out_dir in same directory
            ret = run(f"joern-export --repr cfg --out out_dir".split(), capture_output=True)
            if ret.returncode != 0:
                l.warning("Joern Export failed, stopping CFG extraction")
                return None

            out_dir = Path("./out_dir")
            cfg_files = list(out_dir.rglob("*.dot"))
            for cfg_file in cfg_files:
                cfg = extract_cfg_from_dotfile(cfg_file.absolute())
                if not cfg or not len(cfg.nodes):
                    continue

                if cfg.name in cfgs and len(cfg.nodes) < len(cfgs[cfg.name].nodes):
                    continue

                cfgs[cfg.name] = nx.DiGraph(cfg) #_unparsed_graph_to_supergraph(cfg)

    if lift_cfgs:
        jil_cfgs = {}
        for cfg_name, cfg in cfgs.items():
            jil_cfg = lift_graph(cfg)
            jil_cfg.name = cfg_name
            jil_cfgs[cfg_name] = to_jil_supergraph(jil_cfg)

        cfgs = jil_cfgs

    for _,cfg in cfgs.items():
        node_attrs = {}
        for node in cfg.nodes:
            node_attrs[node] = {'addr': node.addr}
        nx.set_node_attributes(cfg, node_attrs)

    return cfgs


def extract_cfg_from_dotfile(filepath: Path):
    filepath = Path(filepath).expanduser().absolute()
    with open(filepath, "r") as fp:
        data = fp.read()

    try:
        graph = nx.nx_agraph.from_agraph(pg.AGraph(data))
    except Exception:
        graph = None

    return graph

#
# JIL Graph Helpers
#


def merge_jil_nodes(graph: DiGraph, node_a, node_b):
    in_edges = list(graph.in_edges(node_a, data=True))
    out_edges = list(graph.out_edges(node_b, data=True))

    new_node = node_a.copy()
    old_node = node_b
    new_node.statements += old_node.statements

    graph.remove_node(node_a)
    graph.remove_node(node_b)

    if new_node is not None:
        graph.add_node(new_node)

        for src, _, data in in_edges:
            if src is node_b:
                src = new_node
            graph.add_edge(src, new_node, **data)

        for _, dst, data in out_edges:
            if dst is node_a:
                dst = new_node
            graph.add_edge(new_node, dst, **data)

    return new_node


def to_jil_supergraph(graph: DiGraph):
    new_graph = DiGraph(graph)
    while True:
        for src, dst in new_graph.edges():
            if len(list(new_graph.successors(src))) == 1 and len(list(new_graph.predecessors(dst))) == 1:
                merge_jil_nodes(new_graph, src, dst)
                break
        else:
            break

    return new_graph

#
# Unparsed JOERN Graph Helpers
#

def _merge_unparsed_joern_nodes(graph: DiGraph, node_a, node_b, node_data):
    in_edges = list(graph.in_edges(node_a))
    out_edges = list(graph.out_edges(node_b))

    new_node = node_a
    node_data[node_a] += f"\n{node_data[node_b]}"
    del node_data[node_b]

    graph.remove_node(node_a)
    graph.remove_node(node_b)

    if new_node is not None:
        graph.add_node(node_a)

        for src, _ in in_edges:
            if src is node_b:
                src = new_node
            graph.add_edge(src, new_node)

        for _, dst in out_edges:
            if dst is node_a:
                dst = new_node
            graph.add_edge(new_node, dst)

    return new_node


def _unparsed_graph_to_supergraph(graph: DiGraph):
    new_graph = DiGraph(graph)
    node_data = {node: graph._node[node]['label'] for node in new_graph.nodes}
    while True:
        for src, dst in new_graph.edges():
            if len(list(new_graph.successors(src))) == 1 and len(list(new_graph.predecessors(dst))) == 1:
                _merge_unparsed_joern_nodes(new_graph, src, dst, node_data)
                break
        else:
            break

    # assign data
    node_data = {k: {"label": v} for k,v in node_data.items()}
    networkx.set_node_attributes(new_graph, node_data)

    return new_graph

#
# Extras
#


def _nx_to_simple_graph(graph: Graph):
    v_label_to_id = {}
    vertexs = {}
    edges = {}

    for i, node in enumerate(graph.nodes):
        v_label_to_id[str(node)] = i
        vertexs[i] = str(node)

    for i, edge in enumerate(graph.edges):
        src, dst, _ = edge
        src_id = v_label_to_id[src]
        dst_id = v_label_to_id[dst]
        edges[i] = (src_id, dst_id)

    output_str = f"t # {graph.name}\n"
    for i, v in vertexs.items():
        output_str += f"v {i} {v}\n"

    for i, e in edges.items():
        output_str += f"e {e[0]} {e[1]} {i}\n"

    return output_str


def cfg_to_png(cfg, output_path: Path):
    tmp_path = output_path.with_suffix(".dot")
    nx.drawing.nx_agraph.write_dot(cfg, str(tmp_path))
    dot_src = graphviz.Source(open(tmp_path).read(), format="png")
    dot_src.render(outfile=str(output_path.with_suffix(".png")))
    tmp_path.with_suffix(".gv").unlink()
    tmp_path.unlink()


def output_cfg_png(cfg_graph, src_type):
    filename = f"{src_type}_{cfg_graph.name}"
    print(f"[DEBUG] number of nodes - {src_type}: {len(cfg_graph.nodes)}")

    try:
        nx.drawing.nx_agraph.write_dot(cfg_graph, f"{filename}.dot")
        dot_src = graphviz.Source(open(f"{filename}.dot").read(), format="png")
        dot_src.render(outfile=f"{filename}.png")

        run(f"rm {filename}.dot".split())
        run(f"rm {filename}.gv".split())
        print(f"[DEBUG] saved rendered CFG: {filename}.png")
    except Exception as e:
        print(f"[DEBUG] unable to rendered CFG: {filename}.dot")
        print("ERROR", e)
        print(f"[DEBUG] {e}")