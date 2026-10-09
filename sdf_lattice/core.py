"""Directed graph and deterministic topological execution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .nodes.base import Node

@dataclass(frozen=True)
class Edge:
    source: str
    source_port: str
    target: str
    target_port: str

class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node) -> None:
        if node.node_id in self.nodes:
            raise ValueError(f"duplicate node id: {node.node_id}")
        self.nodes[node.node_id] = node

    def connect(self, source: str, source_port: str, target: str, target_port: str) -> Edge:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("both source and target nodes must exist")
        edge = Edge(source, source_port, target, target_port)
        self.edges.append(edge)
        return edge

    def _order(self) -> List[str]:
        incoming = {n: 0 for n in self.nodes}
        outgoing = {n: [] for n in self.nodes}
        for e in self.edges:
            incoming[e.target] += 1
            outgoing[e.source].append(e.target)
        queue = sorted(n for n, count in incoming.items() if count == 0)
        result = []
        while queue:
            current = queue.pop(0)
            result.append(current)
            for target in sorted(outgoing[current]):
                incoming[target] -= 1
                if incoming[target] == 0:
                    queue.append(target)
        if len(result) != len(self.nodes):
            raise ValueError("graph contains a cycle")
        return result

    def run(self, initial: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
        # Initialize the value dictionaries for all node inputs and outputs
        values: Dict[str, Dict[str, Any]] = {
            k: dict(v) for k, v in (initial or {}).items()
        }
        for node_id in self.nodes:
            if node_id not in values:
                values[node_id] = {}

        # Execute in topological order
        for node_id in self._order():
            node = self.nodes[node_id]
            node_inputs = values.get(node_id, {})
            
            try:
                outputs = node.compute(node_inputs)
            except Exception as e:
                raise RuntimeError(f"Execution failed at Node '{node_id}': {e}") from e

            # Update results and track computed keys of the current node
            if outputs:
                values[node_id].update(outputs)

            # Forward outputs to the input ports of connected nodes
            for e in self.edges:
                if e.source == node_id:
                    if e.source_port not in outputs:
                        raise KeyError(f"missing output port: {node_id}.{e.source_port}")
                    values.setdefault(e.target, {})[e.target_port] = outputs[e.source_port]

        return values

NodeGraph = Graph
