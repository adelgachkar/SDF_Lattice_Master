"""Simulation script for Multi-Void Supercell Phase Locking in SDF Theory."""

import json
import numpy as np
from sdf_lattice.nodes.supercell_coupling import SupercellCouplingNode


def simulate_supercell_dynamics(num_voids: int = 5, num_steps: int = 40):
    print("=" * 65)
    print(f"[*] Starting SDF Supercell Simulation: {num_voids} Voids Chain")
    print("=" * 65)

    node = SupercellCouplingNode(
        name="supercell_core",
        params={"inter_coupling_strength": 0.90, "supercell_threshold": 0.70},
    )

    # Initial phase configuration: slightly disturbed uniform phase
    phases = np.zeros((num_voids, 5))
    dt = 0.05
    history = []

    for step in range(num_steps):
        # Physical coupling dynamics: Kuramoto-like phase relaxation between adjacent edges
        # Add slight external strain perturbation at step 15
        perturbation = 0.0
        if 15 <= step <= 22:
            perturbation = 0.25 * np.sin(0.4 * step)

        # Dynamic evolution of void phases towards locked resonance
        for v in range(num_voids):
            for e in range(5):
                coupling_force = 0.0
                if v > 0:
                    coupling_force += np.sin(phases[v - 1, e] - phases[v, e])
                if v < num_voids - 1:
                    coupling_force += np.sin(phases[v + 1, e] - phases[v, e])

                phases[v, e] += dt * (0.85 * coupling_force + perturbation)

        out = node.compute({"void_phase_matrix": phases})
        step_data = {
            "step": step,
            "collective_coherence": round(out["collective_coherence"], 4),
            "inter_cavity_energy": round(out["inter_cavity_energy"], 4),
            "supercell_locked": out["supercell_locked"],
        }
        history.append(step_data)

        if step % 8 == 0 or step == num_steps - 1:
            print(
                f"Step {step:02d} | "
                f"Collective Coherence: {step_data['collective_coherence']:.4f} | "
                f"Inter-Cavity Energy: {step_data['inter_cavity_energy']:.4f} | "
                f"Locked: {step_data['supercell_locked']}"
            )

    print("=" * 65)
    final_state = history[-1]
    print(f"[*] Simulation Complete.")
    print(f"[*] Final Collective State: {'LOCKED_SUPERCELL (BOUND)' if final_state['supercell_locked'] else 'DECOHERED_PHASE_LEAK'}")
    print("=" * 65)


if __name__ == "__main__":
    simulate_supercell_dynamics()
