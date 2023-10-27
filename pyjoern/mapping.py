from pathlib import Path
from typing import Dict
import logging

from cfgutils.sorting import cfg_root_node
import toml
import networkx as nx


l = logging.getLogger(__name__)

def read_line_maps(maps_path: Path, key_is_func=True, value_is_set_type=True):
    with open(maps_path, "r") as fp:
        line_maps = toml.load(fp)

    # convert keys to int and values to set
    if key_is_func:
        for func in line_maps:
            for linenum in list(line_maps[func]):
                if value_is_set_type:
                    line_maps[func][int(linenum)] = set(line_maps[func][linenum])
                else:
                    line_maps[func][int(linenum)] = line_maps[func][linenum]
                del line_maps[func][linenum]
    else:
        for addr in list(line_maps.keys()):
            line_maps[int(addr)] = set(line_maps[addr])
            del line_maps[addr]

    return line_maps


def correct_decompiler_mappings(dec_cfg, dec_line_to_addr_map):
    node = cfg_root_node(dec_cfg)
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

