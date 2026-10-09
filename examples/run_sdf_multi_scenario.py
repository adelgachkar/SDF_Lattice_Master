"""Multi-scenario telemetry runner for SDF Lattice v0.3."""

import os
import csv
import json
import numpy as np

from sdf_lattice.nodes import (
    StrainTensorNode,
    PermittivityEnvelopeNode,
    VoidCouplingNode,
    ClosureConstraintsNode,
)


def run_multi_scenario():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "telemetry_results.csv")
    json_path = os.path.join(output_dir, "telemetry_results.json")

    # Initialize nodes
    strain_node = StrainTensorNode("strain_0", config={"critical_threshold": 0.05})
    perm_node = PermittivityEnvelopeNode("perm_0", params={"epsilon_0": 1.0, "photoelastic_coupling": 0.15})
    coupling_node = VoidCouplingNode("coupling_0", params={"coupling_constant": 1.0, "critical_coherence_threshold": 0.70})
    closure_node = ClosureConstraintsNode("closure_0", params={"min_coherence_threshold": 0.20})

    scenarios = [
        {
            "name": "1_BOUND_STABLE",
            "grad_u": np.array([[0.01, 0.005, 0.0], [0.005, 0.02, 0.0], [0.0, 0.0, -0.015]], dtype=float),
            "edge_phases": [0.10, 0.12, 0.09, 0.11, 0.105],
        },
        {
            "name": "2_PHASE_LEAKAGE",
            "grad_u": np.array([[0.80, 0.40, 0.0], [0.40, 0.90, 0.0], [0.0, 0.0, -0.60]], dtype=float),
            "edge_phases": [0.10, 0.15, 0.12, 0.14, 0.11],
        },
        {
            "name": "3_BIFURCATION",
            "grad_u": np.array([[0.01, 0.005, 0.0], [0.005, 0.02, 0.0], [0.0, 0.0, -0.015]], dtype=float),
            "edge_phases": [0.0, 2 * np.pi / 5, 4 * np.pi / 5, 6 * np.pi / 5, 8 * np.pi / 5],
        },
    ]

    telemetry_data = []

    print("=== SDF LATTICE MULTI-SCENARIO SIMULATION ===")
    for sc in scenarios:
        name = sc["name"]

        # Step 1: Strain
        s_out = strain_node.compute({"displacement_gradient": sc["grad_u"]})

        # Step 2: Permittivity
        p_out = perm_node.compute({
            "trace": s_out["trace"],
            "frobenius_dev": s_out["frobenius_dev"],
            "is_critical": s_out["is_critical"],
        })

        # Step 3: Void Coupling
        c_out = coupling_node.compute({
            "edge_phases": sc["edge_phases"],
            "radiative_flux": p_out["radiative_flux"],
        })

        # Step 4: Closure Constraints (passing phase_coherence)
        cl_out = closure_node.compute({
            "strain_tensor": s_out["strain_tensor"],
            "permittivity_envelope": p_out["effective_permittivity"],
            "coupling_strength": c_out["coupling_energy"],
            "phase_coherence": c_out["phase_coherence"],
        })

        record = {
            "scenario": name,
            "trace": float(s_out["trace"]),
            "frobenius_dev": float(s_out["frobenius_dev"]),
            "effective_permittivity": float(p_out["effective_permittivity"]),
            "radiative_flux": float(p_out["radiative_flux"]),
            "confinement_status": str(p_out["confinement_status"]),
            "phase_coherence": float(c_out["phase_coherence"]),
            "coupling_energy": float(c_out["coupling_energy"]),
            "is_phase_locked": bool(c_out["is_phase_locked"]),
            "causality_residual": float(cl_out["causality_residual"]),
            "energy_deficit": float(cl_out["energy_deficit"]),
            "closure_status": str(cl_out["closure_status"]),
            "is_stable": bool(cl_out["is_stable"]),
        }
        telemetry_data.append(record)

        print(f"\n[{name}]")
        print(f"  Phase Coherence    : {record['phase_coherence']:.4f}")
        print(f"  Causality Residual : {record['causality_residual']:.4f}")
        print(f"  Energy Deficit     : {record['energy_deficit']:.4f}")
        print(f"  Closure Status     : {record['closure_status']}")
        print(f"  Is Stable          : {record['is_stable']}")

    # Save to CSV
    keys = list(telemetry_data[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(telemetry_data)

    # Save to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(telemetry_data, f, indent=2)

    print(f"\n[OK] Telemetry saved to:\n  {csv_path}\n  {json_path}")


if __name__ == "__main__":
    run_multi_scenario()
