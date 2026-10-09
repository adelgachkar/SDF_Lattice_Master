#!/usr/bin/env python3
"""Phase-2 Berry dynamics verification: phase locking, BZ jets, and stability.

Run from any working directory with: python examples/verify_phase2_berry.py
"""
import math
import sys
from pathlib import Path

import numpy as np

# Make the repository importable when this script is invoked by path.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sdf_lattice.nodes.berry_dynamics import BerryDynamicsNode  # noqa: E402


def run_phase2_verification() -> int:
    print("=" * 72)
    print(" SDF-LATTICE PHASE-2 BERRY DYNAMICS VERIFICATION")
    print("=" * 72)

    node = BerryDynamicsNode("phase2-berry-check")

    # Sub-critical input: identical oscillator phases cancel both circulations,
    # locking Delta_gamma to zero and leaving only zero geometric phase leakage.
    subcritical = node.compute({
        "phases": np.zeros(node.N),
        "omega": np.ones(node.N),
        "P_drive": 0.5 * node.P_crit,
        "omega_history": np.ones((60, node.N)),
    })
    sub_geo = subcritical["geometric_phases"]
    sub_jets = subcritical["blandford_znajek_jets"]
    assert abs(sub_geo["delta_gamma"]) <= 1e-12, (
        f"Sub-critical phase difference must lock to 0; got {sub_geo['delta_gamma']}"
    )
    assert sub_geo["gamma_leak"] <= 1e-12, (
        f"Sub-critical phase leak must be minimal (zero within tolerance); got {sub_geo['gamma_leak']}"
    )
    assert not sub_jets["supercritical_state"], "Sub-critical drive must not trigger BZ jets"
    assert sub_jets["jet_total"] == 0.0, "Sub-critical BZ jet power must be zero"
    print("[PASS] Sub-critical Delta_gamma -> 0 and phase leak is minimal")

    # Super-critical input: a 5-fold travelling phase wave gives nonzero chirality.
    phases = np.arange(node.N, dtype=float) * (2.0 * math.pi / node.N)
    omega = np.full(node.N, 2.0)
    # Decaying frequency spread is a deterministic kinetic-locking trajectory.
    offsets = np.array([-0.08, -0.04, 0.0, 0.04, 0.08])
    decay = np.exp(-0.08 * np.arange(60, dtype=float))
    omega_history = 2.0 + decay[:, None] * offsets[None, :]
    drive = 1.5 * node.P_crit
    supercritical = node.compute({
        "phases": phases,
        "omega": omega,
        "P_drive": drive,
        "omega_history": omega_history,
    })
    geo = supercritical["geometric_phases"]
    jets = supercritical["blandford_znajek_jets"]
    stability = supercritical["kinetic_stability"]

    assert abs(geo["delta_gamma"]) > 1e-6, "Travelling phase wave must produce chiral phase asymmetry"
    assert jets["supercritical_state"], "P_drive > P_crit must trigger the super-critical BZ state"
    assert jets["jet_total"] > 0.0, "Super-critical BZ jet emission must have positive power"
    assert jets["jet_north"] >= 0.0 and jets["jet_south"] >= 0.0, "Jet powers must be nonnegative"
    assert math.isclose(jets["jet_north"] + jets["jet_south"], jets["jet_total"], rel_tol=1e-12)
    assert stability["locked"], f"Kinetic stability locking failed: {stability}"
    assert stability["lyapunov_exponent"] < 0.0, "Decaying frequency spread must have negative Lyapunov proxy"
    assert stability["frequency_variance"] < 0.05, "Frequency spread variance exceeds stability bound"
    print("[PASS] Super-critical drive triggers positive Blandford-Znajek jet emission")
    print("[PASS] Kinetic stability locking holds (negative Lyapunov proxy and bounded variance)")
    print(f"      Delta_gamma={geo['delta_gamma']:.6g}, jet_total={jets['jet_total']:.6g}, "
          f"Lyapunov={stability['lyapunov_exponent']:.6g}, "
          f"frequency_variance={stability['frequency_variance']:.6g}")

    print("=" * 72)
    print("PHASE-2 BERRY VERIFICATION: PASS (all assertions passed)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_phase2_verification())
