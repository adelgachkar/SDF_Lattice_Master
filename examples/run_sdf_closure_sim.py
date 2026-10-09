"""
SDF Lattice - Dynamic Simulation & Pipeline Runner (v0.3)
Runs a multi-node pipeline connecting:
StrainTensorNode -> PermittivityEnvelopeNode -> VoidCouplingNode -> ClosureConstraintsNode
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from sdf_lattice.nodes.strain import StrainTensorNode
from sdf_lattice.nodes.permittivity import PermittivityEnvelopeNode
from sdf_lattice.nodes.void_coupling import VoidCouplingNode
from sdf_lattice.nodes.closure_constraints import ClosureConstraintsNode


def run_simulation(steps: int = 5):
    print("=" * 65)
    print(" SDF-Lattice: Multi-Node Pipeline & Closure Dynamic Test")
    print("=" * 65)

    # 1. Initialize all nodes matching v0.3 signatures
    strain_node = StrainTensorNode("strain_0", config={"critical_threshold": 0.05})
    permittivity_node = PermittivityEnvelopeNode("permittivity_0", params={"epsilon_0": 1.0, "photoelastic_coupling": 0.15})
    coupling_node = VoidCouplingNode("coupling_0", params={"coupling_constant": 1.0, "critical_coherence_threshold": 0.7})
    closure_node = ClosureConstraintsNode("closure_0")

    for t in range(1, steps + 1):
        print(f"\n--- [Time Step {t}/{steps}] ---")
        t_factor = t / steps

        # Synthetic displacement gradient matrix (3x3)
        grad_u = np.array([
            [0.01 * t_factor, 0.005, 0.0],
            [0.005, 0.02 * t_factor, 0.0],
            [0.0, 0.0, -0.015 * t_factor]
        ], dtype=float)

        # Step 1: Strain Computation
        strain_in = {"displacement_gradient": grad_u}
        strain_out = strain_node.compute(strain_in)
        strain_tensor = strain_out["strain_tensor"]
        trace = strain_out["trace"]
        frobenius_dev = strain_out["frobenius_dev"]
        is_critical = strain_out["is_critical"]

        print(f"1. Strain: Trace = {trace:.4e}, DevNorm = {frobenius_dev:.4e}, Critical = {is_critical}")

        # Step 2: Permittivity & Radiative Leak Computation
        perm_in = {
            "trace": trace,
            "frobenius_dev": frobenius_dev,
            "is_critical": is_critical
        }
        perm_out = permittivity_node.compute(perm_in)
        eff_eps = perm_out["effective_permittivity"]
        rad_flux = perm_out["radiative_flux"]
        confinement = perm_out["confinement_status"]

        print(f"2. Permittivity: EffEps = {eff_eps:.4f}, RadFlux = {rad_flux:.4e}, Status = {confinement}")

        # Step 3: 5-Edge Cavity Void Coupling
        edge_phases = [
            0.1 * t_factor,
            0.12 * t_factor,
            0.09 * t_factor,
            0.11 * t_factor,
            0.105 * t_factor
        ]
        coupling_in = {
            "edge_phases": edge_phases,
            "radiative_flux": rad_flux
        }
        coupling_out = coupling_node.compute(coupling_in)
        coherence = coupling_out["phase_coherence"]
        coupling_energy = coupling_out["coupling_energy"]
        phase_locked = coupling_out["is_phase_locked"]

        print(f"3. Void Coupling: Coherence = {coherence:.4f}, Energy = {coupling_energy:.4f}, Locked = {phase_locked}")

        # Step 4: Closure & Kinetic Stability Evaluation
        closure_in = {
            "strain_tensor": strain_tensor,
            "permittivity_envelope": eff_eps,
            "coupling_strength": coupling_energy
        }
        closure_out = closure_node.compute(closure_in)
        causality_res = closure_out["causality_residual"]
        energy_def = closure_out["energy_deficit"]
        closure_status = closure_out["closure_status"]
        is_stable = closure_out["is_stable"]

        print(f"4. Closure: Status = {closure_status}, CausalityRes = {causality_res:.4e}, Deficit = {energy_def:.4e}, Stable = {is_stable}")

    print("\n" + "=" * 65)
    print(" Pipeline simulation run completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    run_simulation(steps=5)
