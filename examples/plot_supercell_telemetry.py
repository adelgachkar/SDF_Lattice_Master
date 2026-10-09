"""Build and execute a complete 5-node SDF Lattice pipeline (v0.4 Architecture)."""

import json
from pathlib import Path
import sys

# Ensure root directory in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sdf_lattice.core import NodeGraph
from sdf_lattice.nodes.closure_constraints import ClosureConstraintsNode
from sdf_lattice.nodes.permittivity import PermittivityEnvelopeNode
from sdf_lattice.nodes.strain import StrainTensorNode
from sdf_lattice.nodes.supercell_coupling import SupercellCouplingNode
from sdf_lattice.nodes.void_coupling import VoidCouplingNode


def build_and_run_complete_pipeline():
    print("=" * 70)
    print("[*] Initializing Full SDF Lattice Computational Graph (v0.4)")
    print("=" * 70)

    # 1. Instantiate Graph
    graph = NodeGraph()

    # 2. Add all 5 core nodes with correct signature: name and optional config
    graph.add_node(
        StrainTensorNode(
            name="strain_node",
            config={"shear_modulus": 1.2, "bulk_modulus": 2.5},
        )
    )
    graph.add_node(
        PermittivityEnvelopeNode(
            name="eps_node",
            config={"eps_base": 1.0, "chi_anisotropy": 0.15},
        )
    )
    graph.add_node(
        VoidCouplingNode(
            name="void_node",
            config={"edge_weights": [1.0, 1.0, 1.0, 1.0, 1.0], "leak_rate": 0.02},
        )
    )
    graph.add_node(
        ClosureConstraintsNode(
            name="closure_node",
            config={"min_coherence_threshold": 0.60, "friedmann_coupling": 1.1},
        )
    )
    graph.add_node(
        SupercellCouplingNode(
            name="supercell_node",
            config={
                "inter_coupling_strength": 0.90,
                "supercell_threshold": 0.70,
            },
        )
    )

    print(f"[✓] Added {len(graph.nodes)} physics nodes to graph.")

    # 3. Prepare initial physical inputs for the multi-void lattice
    graph_inputs = {
        "strain_node": {"displacement_gradient": [[0.02, 0.005], [0.005, 0.03]]},
        "eps_node": {"strain_energy": 0.12},
        "void_node": {"edge_phases": [0.05, -0.02, 0.03, -0.01, 0.04]},
        "closure_node": {
            "reactive_energy": 1.45,
            "phase_coherence": 0.98,
            "leakage_flux": 0.015,
        },
        "supercell_node": {
            "void_phase_matrix": [
                [0.05, -0.02, 0.03, -0.01, 0.04],
                [0.06, -0.01, 0.02, -0.02, 0.03],
                [0.04, -0.03, 0.04, -0.01, 0.05],
            ]
        },
    }

    # 4. Compute pipeline
    results = {}
    for node_name, node_obj in graph.nodes.items():
        inputs = graph_inputs.get(node_name, {})
        res = node_obj.compute(inputs)
        results[node_name] = res

    # 5. Formatted Output
    print("\n[+] Computational Graph Execution Summary:")
    print("-" * 70)
    for node_name, res in results.items():
        print(f"Node: [{node_name}]")
        if isinstance(res, dict):
            for k, v in res.items():
                if isinstance(v, float):
                    print(f"   ├─ {k}: {v:.4f}")
                else:
                    print(f"   ├─ {k}: {v}")
        else:
            print(f"   ├─ result: {res}")
    print("=" * 70)

    # Save Pipeline Snapshot
    out_dir = Path("examples/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = out_dir / "pipeline_v04_execution.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            default=lambda o: (
                o.tolist() if hasattr(o, "tolist") else str(o)
            ),
        )

    print(f"[✓] Pipeline execution snapshot saved to: {snapshot_path}")


if __name__ == "__main__":
    build_and_run_complete_pipeline()
