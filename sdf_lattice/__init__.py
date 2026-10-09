"""
sdf_lattice.registry
~~~~~~~~~~~~~~~~~~~~
In-process registry for node factories and concrete node registration.
"""

from typing import Dict, Any, Tuple, Optional


class NodeRegistry:
    def __init__(self):
        self._factories = {}

    def register(self, type_name: str, factory):
        if type_name in self._factories:
            raise ValueError(f"already registered: {type_name}")
        self._factories[type_name] = factory

    def create(self, type_name: str, node_id: str, params: Optional[Dict[str, Any]] = None):
        try:
            factory = self._factories[type_name]
        except KeyError:
            raise KeyError(f"unknown node type: {type_name}")
        return factory(node_id, params)

    def types(self) -> Tuple[str, ...]:
        return tuple(sorted(self._factories))


def register_defaults(registry: NodeRegistry) -> None:
    """Register each built-in concrete node exactly once.

    The abstract Node base is deliberately excluded. Concrete nodes
    are resolved via their declared `type_name` or `NODE_TYPE`,
    falling back to their class name if unspecified.
    """
    from .nodes import (
        StrainTensorNode,
        PermittivityEnvelopeNode,
        VoidCouplingNode,
        ClosureConstraintsNode,
        SupercellCouplingNode,
        PeristalticPumpNode,
        RetardedCausalityNode,
        BerryDynamicsNode,
        BerryTorqueNode,
        CavityResilienceNode,  # <--- ۱. ایمپورت نود جدید پایداری حجم
        PassthroughNode,
    )

    concrete_nodes = (
        StrainTensorNode,
        PermittivityEnvelopeNode,
        VoidCouplingNode,
        ClosureConstraintsNode,
        SupercellCouplingNode,
        PeristalticPumpNode,
        RetardedCausalityNode,
        BerryDynamicsNode,
        BerryTorqueNode,
        CavityResilienceNode,  # <--- ۲. اضافه شدن به لیست نودهای رسمی
        PassthroughNode,
    )

    for cls in concrete_nodes:
        # Read only a class's own declared identifier; inherited "base" is not
        # a usable node type for concrete subclasses.
        type_name = cls.__dict__.get("NODE_TYPE") or cls.__dict__.get("type_name")
        if not type_name or type_name == "base":
            type_name = cls.__name__
        registry.register(type_name, cls)
