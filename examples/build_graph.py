"""
Build and execute the SDF Lattice Computational Graph Pipeline.
Pipeline v0.4 - Full Multi-Node Physics Integration
"""

import json
import math
from pathlib import Path
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sdf_lattice.core import Graph
from sdf_lattice.nodes.strain import StrainTensorNode
from sdf_lattice.nodes.permittivity import PermittivityEnvelopeNode
from sdf_lattice.nodes.void_coupling import VoidCouplingNode
from sdf_lattice.nodes.closure_constraints import ClosureConstraintsNode


def main():
    print("=" * 75)
    print("[*] Initializing Complete SDF Lattice Computational Graph")
    print("=" * 75)

    # 1. Instantiate Graph
    graph = Graph()

    # 2. Instantiate Physical Nodes (node_id, params)
    strain = StrainTensorNode("strain", {"critical_threshold": 0.5})
    permittivity = PermittivityEnvelopeNode("permittivity", {"alpha": 0.1, "beta": 0.85})
    void_coupling = VoidCouplingNode("void_coupling", {})
    closure = ClosureConstraintsNode("closure", {})

    graph.add_node(strain)
    graph.add_node(permittivity)
    graph.add_node(void_coupling)
    graph.add_node(closure)

    # 3. Connect Graph Ports
    # Strain -> Permittivity
    graph.connect("strain", "trace", "permittivity", "trace")
    graph.connect("strain", "frobenius_dev", "permittivity", "frobenius_dev")
    graph.connect("strain", "is_critical", "permittivity", "is_critical")

    # Permittivity -> Void Coupling (Radiative flux injection)
    graph.connect("permittivity", "radiative_flux", "void_coupling", "radiative_flux")

    # Connect to Closure Constraints Node
    graph.connect("strain", "strain_tensor", "closure", "strain_tensor")
    graph.connect("permittivity", "effective_permittivity", "closure", "permittivity_envelope")
    graph.connect("void_coupling", "coupling_energy", "closure", "coupling_strength")

    # 4. Input Boundary Conditions
    # - 2x2 Traceless Shear Tensor
    # - 5-Edge Pentagon Phase Array [phi_0 ... phi_4]
    inputs = {
        "strain": {
            "tensor": [
                [1.0, 0.0],
                [0.0, -1.0]
            ]
        },
        "void_coupling": {
            "edge_phases": [0.0, 0.05, -0.02, 0.01, -0.04]
        }
    }

    # 5. Execute Graph
    results = graph.run(inputs)

    print("\n[+] Computational Graph Execution Succeeded! Full Telemetry Snapshot:")
    print("-" * 75)
    print(json.dumps(results, indent=2))
    print("=" * 75)

    # 6. Save execution snapshot
    out_dir = Path("examples/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "pipeline_v04_full_execution.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Full execution snapshot saved to: {out_file}")


if __name__ == "__main__":
    main()
