import itertools
from pathlib import Path
from typing import Dict, Union, List, Set, Optional
import logging

import networkx as nx
from cfgutils.regions.region_identifier import RegionIdentifier
from cfgutils.regions.graph_region import GraphRegion

from .ged import graph_edit_distance
from .utils import addr_to_node_map, to_jil_supergraph, output_cfg_png
from .jil.block import Block, make_merge_block, MergedRegionStart

l = logging.getLogger(__name__)
_DEBUG = False
if _DEBUG:
    l.setLevel(logging.DEBUG)

MAX_EXACT_GED_SIZE = 8


def destroy_old_region(cfg: nx.DiGraph, expanded_region_graph: nx.DiGraph, r_head: Block):
    extra_edge_points = 0
    r_nodes = list(expanded_region_graph.nodes)
    if r_head not in r_nodes:
        r_nodes.append(r_head)

    r_preds = list()
    r_succs = list()

    for r_node in r_nodes:
        for suc in cfg.successors(r_node):
            if suc not in r_nodes:
                r_succs.append(suc)
                extra_edge_points += 1
        for pred in cfg.predecessors(r_node):
            if pred not in r_nodes:
                r_preds.append(pred)
                extra_edge_points += 1

    cfg.remove_nodes_from(r_nodes)
    merged_node = make_merge_block(r_head.addr, r_nodes)
    cfg.add_node(merged_node)
    for pred in r_preds:
        cfg.add_edge(pred, merged_node)

    for suc in r_succs:
        cfg.add_edge(merged_node, suc)

    return extra_edge_points


def expand_region_to_block_graph(region: GraphRegion, graph: nx.DiGraph):
    def _expand_region_to_blocks(_region: GraphRegion):
        all_nodes = list()
        for node in _region.graph.nodes:
            if isinstance(node, Block):
                all_nodes.append(node)
            elif isinstance(node, GraphRegion):
                all_nodes += _expand_region_to_blocks(node)

        return all_nodes

    region_blocks = _expand_region_to_blocks(region)
    return nx.subgraph(graph, region_blocks)


def expand_region_head_to_block(region: GraphRegion):
    region_head = region.head
    if isinstance(region_head, Block):
        return region_head

    if isinstance(region_head, GraphRegion):
        return expand_region_head_to_block(region_head)

    raise ValueError(f"Invalid region head type {type(region_head)}")

def is_only_blocks(region: GraphRegion):
    for node in region.graph.nodes:
        if isinstance(node, Block):
            continue
        if isinstance(node, GraphRegion):
            return False

    return True


def find_containing_block_addrs(graph: nx.DiGraph, lines: Set):
    containing_addrs = set()
    line_has_container = set()
    graph_nodes = list(graph.nodes)
    for node in graph_nodes:
        for line in lines:
            if node.contains_addr(line):
                line_has_container.add(line)
                containing_addrs.add(node.addr)

    for line in lines:
        if line in line_has_container:
            continue

        closest_node = min(graph_nodes, key=lambda x: x.addr)
        for node in graph_nodes:
            if line >= node.addr >= closest_node.addr:
                closest_node = node

        containing_addrs.add(closest_node.addr)
    return containing_addrs


def find_matching_regions_with_lines(region: GraphRegion, lines: Set):
    if region.head.addr in lines:
        yield region
    
    for node in region.graph.nodes:
        if isinstance(node, Block):
            continue
        if isinstance(node, GraphRegion):
            yield from find_matching_regions_with_lines(node, lines)


def dfs_region_for_parent(region: GraphRegion, child: Block):
    for node in region.graph.nodes:
        if isinstance(node, GraphRegion):
            if node.head.addr == child.addr:
                yield region

            yield from dfs_region_for_parent(node, child)


def dfs_region_for_leafs(region: GraphRegion):
    has_block = False
    only_blocks = True
    for node in region.graph.nodes:
        if isinstance(node, GraphRegion):
            yield from dfs_region_for_leafs(node)
            only_blocks = False
        elif isinstance(node, Block):
            has_block = True

    if only_blocks and has_block:
        yield region


def find_some_leaf_region(region: Union[Block, GraphRegion], node_blacklist, og_cfg: nx.DiGraph) -> Optional[Union[GraphRegion, Block]]:
    # sanity check
    if isinstance(region, Block):
        return region
    elif not isinstance(region, GraphRegion):
        return None

    leaf_regions = list(dfs_region_for_leafs(region))
    if not leaf_regions:
        return None

    # find a region we did not blacklist
    leaf_regions = sorted(leaf_regions, key=lambda x: x.head.addr, reverse=True)
    for leaf_region in leaf_regions:
        if leaf_region.head.addr not in node_blacklist:
            return leaf_region

    # if we are all out of non blacklisted regions, let's try to find a parent of each leaf
    #for leaf_region in leaf_regions:
    #    head, graph = leaf_region
    #    parents = list(dfs_region_for_parent(region, head))
    #    if not parents:
    #        continue

    #    parents = sorted(parents, key=lambda x: x.head.addr)
    #    for parent in parents:
    #        if parent.head.addr in node_blacklist:
    #            continue

    #        expanded_parent = expand_region_to_block_graph(parent, og_cfg)
    #        return parent.head, expanded_parent

    return None


def cfg_edit_distance(
        dec_cfg: nx.DiGraph,
        src_cfg: nx.DiGraph,
        dec_line_to_addr_map: Dict,
        src_addr_to_line_map: Dict,
        max_region_collapse=200,
        max_region_estimates=3,
):
    """
    src_addr_to_line_map[address] = set(line1, line2, ...)
    dec_line_to_addr_map[line_num] = set(addr1, addr2, ...)

    :param src_cfg:
    :param dec_cfg:
    :param src_addr_to_line_map:
    :param dec_line_to_addr_map:
    :param max_region_collapse:
    :return:
    """
    src_cfg, dec_cfg = nx.DiGraph(src_cfg), nx.DiGraph(dec_cfg)
    cfged_score = 0
    curr_region_collapse = 0
    curr_region_estimates = 0
    redo_structuring = True
    region_blacklist = set()

    if len(src_cfg.nodes) <= MAX_EXACT_GED_SIZE and len(dec_cfg.nodes) <= MAX_EXACT_GED_SIZE:
        l.debug(f"Graph small enough for exact! Running it...")
        return graph_edit_distance(dec_cfg, src_cfg, with_timeout=10, max_on_timeout=False)

    while True:
        l.debug(f"Running region collapse round {curr_region_collapse}...")
        if curr_region_collapse >= max_region_collapse:
            l.debug(f"Max region collapse limit hit. Exiting early with max score!")
            return cfged_score + len(src_cfg.nodes) + len(dec_cfg.nodes) + len(src_cfg.edges) + len(dec_cfg.edges)
        
        # supergraph it!
        if redo_structuring:
            #src_cfg, dec_cfg = to_jil_supergraph(src_cfg), to_jil_supergraph(dec_cfg)
            src_nodes, dec_nodes = addr_to_node_map(src_cfg), addr_to_node_map(dec_cfg)
            l.debug(f"Decompiler nodes: {len(dec_cfg.nodes)}")
            l.debug(f"Source nodes: {len(src_cfg.nodes)}")

            # compute the regions
            src_regions, dec_regions = RegionIdentifier(src_cfg).region, RegionIdentifier(dec_cfg).region

        # Now that you have regions we want to iteratively enter the lower region we can find on one graph
        # then find that same region on the other graph, then do a graph edit distance. In this case
        # we start with the src cfg
        dec_region = find_some_leaf_region(dec_regions, region_blacklist, dec_cfg)
        if dec_region is None:
            dec_r_head, dec_r_cfg = None, None
        elif isinstance(dec_region, Block):
            dec_r_head, dec_r_cfg = dec_region, nx.DiGraph()
            dec_r_cfg.add_node(dec_region)
        else:
            dec_r_head, dec_r_cfg = dec_region.head, dec_region.graph

        if dec_r_head is None:
            l.debug(f"We are unable to match anymore small region heads, which means we must now approximate the rest.")
            cfged_score += graph_edit_distance(dec_cfg, src_cfg, with_timeout=8, max_on_timeout=False)
            break

        # map the decompilation line to an address (reported by the decompiler
        addrs = dec_line_to_addr_map.get(dec_r_head.addr, None)
        if not addrs:
            # quick check if you can find the line in the addr map in a proximity
            up_addrs = dec_line_to_addr_map.get(dec_r_head.addr - 1, None)
            down_addrs = dec_line_to_addr_map.get(dec_r_head.addr + 1, None)
            if not up_addrs and not down_addrs:
                l.debug(f"Unable to find any line-addr map for region head {dec_r_head.addr}! Skipping...")
                region_blacklist.add(dec_r_head.addr)
                continue

            addrs = up_addrs if up_addrs else down_addrs

        all_lines = set(
            itertools.chain.from_iterable(
                [src_addr_to_line_map[addr] for addr in addrs if addr in src_addr_to_line_map]
            )
        )
        lines_in_src = set(filter(lambda x: x in src_nodes, all_lines))

        # We were unable to find a real region start, probably because a node got consumed
        if not lines_in_src:
            lines_in_src = find_containing_block_addrs(src_cfg, all_lines)
            if not lines_in_src and addrs:
                # If we still have nothing, walk backwards!
                for i in range(1, 0x14):
                    all_lines = set(
                        itertools.chain.from_iterable(
                            [src_addr_to_line_map[addr-i] for addr in addrs if addr-i in src_addr_to_line_map]
                        )
                    )
                    lines_in_src = set(filter(lambda x: x in src_nodes, all_lines))
                    if lines_in_src:
                        break


        lines_in_src = sorted(lines_in_src)
        matching_src_regions = list(find_matching_regions_with_lines(src_regions, lines_in_src))
        if not matching_src_regions:
            region_blacklist.add(dec_r_head.addr)
            redo_structuring = False
            curr_region_collapse += 1
            l.debug(f"Unable to find a pairing region for {dec_r_head.addr}: no src addrs found")
            continue

        #
        # try to find the base matching region
        #

        # gather sizes
        matches_by_size = {}
        lowest_size = 10000
        for src_region in matching_src_regions:
            src_block_region = expand_region_to_block_graph(src_region, src_cfg)
            src_r_head = src_region.head
            size_diff = abs(len(src_block_region.nodes) - len(dec_r_cfg.nodes))
            matches_by_size[src_r_head] = (src_region, size_diff)
            if size_diff < lowest_size:
                lowest_size = size_diff

        # filter out the ones that are too big
        matching_src_regions = list(filter(lambda x: x[1][1] <= lowest_size, matches_by_size.items()))
        if not matching_src_regions:
            region_blacklist.add(dec_r_head.addr)
            redo_structuring = False
            curr_region_collapse += 1
            l.debug(f"Unable to find a pairing region for {dec_r_head.addr}")
            continue

        # if we have more than one, tie break with statement size
        best_match = None
        if len(matching_src_regions) > 1:
            smallest_stmt_size = 10000
            for (head, (region, size)) in matching_src_regions:
                if not isinstance(head, Block):
                    continue

                has_merged_region = isinstance(head.statements[0], MergedRegionStart)
                if len(head.statements) < smallest_stmt_size:
                    smallest_stmt_size = len(head.statements)
                    best_match = region

                if has_merged_region:
                    best_match = region
                    break

        if best_match is None:
            best_match = matching_src_regions[0][1][0]


        l.debug(f"Collapsing (Dec, Src) region pair: {(dec_r_head, best_match.head)}")
        #
        # compute GED of the expanded region
        #

        src_r_cfg = expand_region_to_block_graph(best_match, src_cfg)

        dec_r_size, src_r_size = len(dec_r_cfg.nodes), len(src_r_cfg.nodes)
        if dec_r_size > MAX_EXACT_GED_SIZE or src_r_size > MAX_EXACT_GED_SIZE:
            l.debug(f"Encountered a region too large (dec,src): ({len(dec_r_cfg.nodes), len(src_r_cfg.nodes)} nodes) for an exact score, estimating it...")
            size_diff = abs(dec_r_size - src_r_size)
            curr_region_collapse += 1
            if size_diff > dec_r_size*2 or size_diff > src_r_size*2:
                l.debug(f"Difference in regions size too large to approximate, skipping for now...")
                region_blacklist.add(dec_r_head.addr)
                redo_structuring = False
                continue

            #if curr_region_estimates >= max_region_estimates:
            #    l.warning(f"Exceeded the max region GED approximizaition limit. This function can't be computed.")
            #    return -1
            curr_region_estimates += 1

        distance = graph_edit_distance(dec_r_cfg, src_r_cfg, with_timeout=2)
        cfged_score += distance
        l.debug(f"Region distance: {distance}")

        #
        # cleanup, destroy measured nodes, and restart loop
        #

        extra_src_edges = destroy_old_region(
            src_cfg,
            expand_region_to_block_graph(best_match, src_cfg),
            expand_region_head_to_block(best_match)
        )
        extra_dec_edges = destroy_old_region(
            dec_cfg,
            expand_region_to_block_graph(dec_region, dec_cfg) if not isinstance(dec_region, Block) else dec_region,
            expand_region_head_to_block(dec_region) if not isinstance(dec_region, Block) else dec_region
        )
        edge_diff = abs(extra_src_edges - extra_dec_edges)
        if edge_diff:
            l.debug(f"In/Out Edge Diff: {edge_diff}")
            cfged_score += edge_diff

        if len(dec_cfg.nodes) <= 1 or len(src_cfg.nodes) <= 1:
            cfged_score += graph_edit_distance(dec_cfg, src_cfg)
            break

        region_blacklist = set()
        curr_region_collapse += 1
        redo_structuring = True

    l.debug(f"Final CFGED Score: {cfged_score}")
    return cfged_score



