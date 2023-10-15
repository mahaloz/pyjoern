from textwrap import dedent
from typing import Union, List

import networkx as nx
from cfgutils.data import GenericBlock

from .statement import MergedRegionStart


class Block(GenericBlock):
    def __repr__(self):
        return f"<Block: {self.addr}{self._idx_str}, {len(self.statements)} statements>"

    def __str__(self):
        output = f"{self.addr}{self._idx_str}:\n"
        for line in self.statements:
            output += f"{line}\n"

        return output

    def contains_addr(self, addr):
        if self.addr == addr:
            return True
        
        for stmt in self.statements:
            if stmt.source_line_number == addr:
                return True

        return False

    @classmethod
    def merge_many_blocks(cls, start_addr, nodes: List["GenericBlock"]):
        node_count = 0
        stmts = list()
        for node in nodes:
            for stmt in node.statements:
                node_count += stmt.total_nodes if isinstance(stmts, MergedRegionStart) else 1
                stmts.append(stmt)

        return Block(
            start_addr,
            statements=[MergedRegionStart(source_line_number=start_addr, total_nodes=node_count)] + stmts,
            is_merged_node=True,
        )
