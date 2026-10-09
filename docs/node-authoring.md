# SDF Lattice: Node Authoring Guide

This guide describes how to implement and register custom computational nodes in the `sdf_lattice` DAG framework.

## 1. Node Base Architecture

Computational blocks inherit from `sdf_lattice.nodes.base.Node`. Check the actual base class in the repository for required constructor arguments and interfaces; a typical node implements `compute(inputs)` and returns a dictionary of outputs.

```python
from sdf_lattice.nodes.base import Node

class CustomNode(Node):
    def compute(self, inputs: dict) -> dict:
        return {"output": inputs.get("input", 0.0)}
```

## 2. Implementation Guidelines

1. Prefer stateless computations; pass state through explicit inputs or supported feedback edges.
2. Use vectorized NumPy operations for array workloads and preserve appropriate real or complex dtypes.
3. Respect the framework's causal and boundary constraints when implementing time-dependent propagation.
4. Validate inputs and document output names, expected shapes, and units.

## 3. Node Registration

If configuration-driven construction is supported, import and add the custom node to the registry in `sdf_lattice/registry.py`, following the patterns used by existing nodes. Add focused unit tests under `tests/` and run `pytest`.
