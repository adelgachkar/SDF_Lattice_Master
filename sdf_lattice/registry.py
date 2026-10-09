"""Optional in-process registry for node factories."""
class NodeRegistry:
    def __init__(self): self._factories = {}
    def register(self, type_name, factory):
        if type_name in self._factories: raise ValueError(f"already registered: {type_name}")
        self._factories[type_name] = factory
    def create(self, type_name, node_id, params=None):
        try: factory = self._factories[type_name]
        except KeyError: raise KeyError(f"unknown node type: {type_name}")
        return factory(node_id, params)
    def types(self): return tuple(sorted(self._factories))


def register_defaults(registry) -> None:
    """Register each built-in concrete node exactly once.

    The abstract Node base is deliberately excluded. Some older concrete node
    classes inherit its ``type_name = "base"``; use their class name as a
    unique fallback rather than registering multiple factories as ``base``.
    """
    from .nodes import (
        StrainTensorNode, PermittivityEnvelopeNode, VoidCouplingNode,
        ClosureConstraintsNode, SupercellCouplingNode, PeristalticPumpNode,
        RetardedCausalityNode, BerryDynamicsNode, BerryTorqueNode, PassthroughNode,
    )
    concrete_nodes = (
        StrainTensorNode, PermittivityEnvelopeNode, VoidCouplingNode,
        ClosureConstraintsNode, SupercellCouplingNode, PeristalticPumpNode,
        RetardedCausalityNode, BerryDynamicsNode, BerryTorqueNode, PassthroughNode,
    )
    for cls in concrete_nodes:
        # Read only a class's own declared identifier; inherited "base" is not
        # a usable node type for concrete subclasses.
        type_name = cls.__dict__.get("NODE_TYPE") or cls.__dict__.get("type_name")
        if not type_name or type_name == "base":
            type_name = cls.__name__
        registry.register(type_name, cls)
