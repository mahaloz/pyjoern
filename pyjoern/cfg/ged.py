import re
from collections import defaultdict
import logging

import networkx as nx

from .jil.block import Block
from .jil.statement import (
    Statement, Assignment, Compare, Call
)
from .utils import find_function_root_node
from ..utils import timeout

_l = logging.getLogger(__name__)

#
# Edit distance
#


def upper_bound_ged(g1, g2, with_timeout=10):
    try:
        with timeout(seconds=with_timeout):
            dist = next(nx.optimize_graph_edit_distance(g1, g2))
    except TimeoutError:
        dist = None

    return dist


def graph_edit_distance(g1, g2, with_timeout=10, max_on_timeout=True):
    if g1 is None or g2 is None:
        return None

    g1_start, g2_start = find_function_root_node(g1), find_function_root_node(g2)
    if g1_start is not None and g2_start is not None:
        roots = (g1_start, g2_start,)
    else:
        roots = None
    
    if max_on_timeout:
        try:
            with timeout(seconds=with_timeout):
                dist = nx.graph_edit_distance(g1, g2, roots=roots)
        except TimeoutError:
            _l.debug(f"Although in exact_ged range, there was still a timeout on {g1.name}... giving max score.")
            dist = None

    else:
        try:
            with timeout(seconds=with_timeout*3):
                dist = nx.graph_edit_distance(g1, g2, roots=roots, timeout=with_timeout)
        except TimeoutError:
            _l.debug(f"Although in attempted to get an approximation, the internal GED algo took 3 times timeout... giving max score.")
            dist = None

    if dist is None:
        dist = len(g1.nodes) + len(g1.edges) + len(g2.nodes) + len(g2.edges)
    return dist


#
# Similarity Helpers
#

def find_unique_consts(graph: nx.DiGraph):
    const_count = defaultdict(int)
    for node in graph.nodes:
        node: Block = node

        for stmt in node.statements:
            stmt: Statement = stmt

            if isinstance(stmt, Assignment):
                consts = [stmt.dst]
            elif isinstance(stmt, Call):
                consts = stmt.args
            elif isinstance(stmt, Compare):
                consts = [stmt.arg2]
            else:
                continue

            for const in consts:
                try:
                    maybe_number = int(const.replace("u", ""), 0)
                except Exception:
                    maybe_number = None

                if maybe_number is not None:
                    const_count[maybe_number] += 1
                    continue

                maybe_str = re.findall('".*"', const)
                if maybe_str:
                    const_count[maybe_str[0]] +=1
                    continue

                maybe_char = re.findall("'[a-zA-Z0-9]'", const)
                if maybe_char:
                    const_count[maybe_char[0]] += 1
                    continue

    unique_consts = list()
    for const, count in const_count.items():
        if count > 1:
            continue

        unique_consts.append(const)

    return set(unique_consts)


def find_unique_calls(graph: nx.DiGraph):
    call_count = defaultdict(int)
    for node in graph.nodes:
        node: Block = node

        for stmt in node.statements:
            if not isinstance(stmt, Call):
                continue

            call_count[stmt.func] += 1

    return set([
        func for func, count in call_count.items() if count == 1
    ])


def find_matching_nodes(graph1: nx.DiGraph, graph2: nx.DiGraph):
    matching_blocks = list()

    # unique consts
    unique_consts = find_unique_consts(graph1).intersection(find_unique_consts(graph2))
    for const in unique_consts:
        pair = []
        for graph in (graph1, graph2):
            found = False
            for node in graph.nodes:
                for stmt in node.statements:
                    if isinstance(stmt, Assignment):
                        found = str(const) in stmt.dst
                    elif isinstance(stmt, Call):
                        found = str(const) in stmt.args
                    elif isinstance(stmt, Compare):
                        found = str(const) in stmt.arg2

                    if found:
                        break
                if found:
                    break
            else:
                _l.debug("WARNING, did not find a node we should've")
                break

            pair.append(node)
        matching_blocks.append(pair)

    return matching_blocks


