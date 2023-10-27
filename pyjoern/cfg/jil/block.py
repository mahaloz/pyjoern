from textwrap import dedent
from typing import Union, List

from cfgutils.data import GenericBlock
from .statement import MergedRegionStart, Nop


class Block(GenericBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_merged_node = kwargs.get("is_merged_node", False)
        self._is_entrypoint = kwargs.get("is_entrypoint", False)
        self._is_exitpoint = kwargs.get("is_exitpoint", False)

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

    @property
    def is_merged_node(self):
        if self._is_merged_node:
            return True

        return self.statements and isinstance(self.statements[0], MergedRegionStart)

    @is_merged_node.setter
    def is_merged_node(self, data):
        self._is_merged_node = data

    @property
    def is_entrypoint(self):
        if self._is_entrypoint:
            return True

        if not self.statements:
            return False

        first_stmt = self.statements[0]
        if isinstance(first_stmt, MergedRegionStart):
            for stmt in self.statements:
                if isinstance(stmt, Nop) and stmt.type == Nop.FUNC_START:
                    return True
        elif isinstance(first_stmt, Nop) and first_stmt.type == Nop.FUNC_START:
            return True
        else:
            return False

    @is_entrypoint.setter
    def is_entrypoint(self, data):
        self._is_entrypoint = data

    @property
    def is_exitpoint(self):
        if self._is_exitpoint:
            return True

        if not self.statements:
            return False

        last_stmt = self.statements[-1]
        first_stmt = self.statements[0]
        if isinstance(last_stmt, Nop) and last_stmt.type == Nop.FUNC_END:
            return True
        elif isinstance(first_stmt, MergedRegionStart):
            for stmt in self.statements:
                if isinstance(stmt, Nop) and stmt.type == Nop.FUNC_END:
                    return True
        else:
            return False

    @is_exitpoint.setter
    def is_exitpoint(self, data):
        self._is_exitpoint = data

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

