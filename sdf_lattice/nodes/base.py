"""Base contract for received or user-authored nodes."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

class Node(ABC):
    """A stateless-by-default graph node with named inputs and outputs."""
    type_name = "base"

    def __init__(self, node_id: str, params: Dict[str, Any] | None = None):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("node_id must be a non-empty string")
        self.node_id = node_id
        self.params = dict(params or {})

    @abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return output-port values for the supplied input-port values."""
        raise NotImplementedError

    def describe(self) -> Dict[str, Any]:
        return {"id": self.node_id, "type": self.type_name, "params": self.params}

class PassthroughNode(Node):
    """Useful placeholder: copies all inputs to outputs."""
    type_name = "passthrough"
    def compute(self, inputs):
        return dict(inputs)
