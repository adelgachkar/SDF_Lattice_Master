"""Peristaltic pump node with optional phase-budgeted smoothing.

The legacy calculation and its five output keys remain the default. Enable
``quasi_continuous_coupling`` in node params to apply the opt-in phase budget.
"""
from typing import Any, Dict
import math
import numpy as np
from .base import Node

CONTINUUM_PHASE_LAG = 0.032
SAMPLING_TICK_GAP = 0.004
CONTRAST_RATIO = CONTINUUM_PHASE_LAG / SAMPLING_TICK_GAP


def quasi_continuous_coupling(
    amplitude: float,
    phase: float,
    dt: float,
    tau_relax: float = CONTINUUM_PHASE_LAG,
) -> float:
    """Return a cosine carrier with exponential, non-negative-time smoothing."""
    amplitude, phase, dt, tau_relax = map(float, (amplitude, phase, dt, tau_relax))
    if not all(map(math.isfinite, (amplitude, phase, dt, tau_relax))):
        raise ValueError("coupling arguments must be finite")
    if tau_relax <= 0.0:
        return amplitude * math.cos(phase)
    scale = -math.expm1(-max(dt, 0.0) / tau_relax)
    return amplitude * scale * math.cos(phase)


class PeristalticPumpNode(Node):
    """Computes pump thrust, torsional torque, and residual dissipation."""
    NODE_TYPE = "PeristalticPumpNode"

    def __init__(self, node_id: str, params: Dict[str, Any] | None = None) -> None:
        super().__init__(node_id, params)
        self.angular_deficit_deg = float(self.params.get("angular_deficit_deg", 7.36))
        self.kappa_torsion = float(self.params.get("kappa_torsion", 1.37))
        self.compaction_density = float(self.params.get("compaction_density", 5.0))
        self.alpha_screening = float(self.params.get("alpha_screening", 2.0 / 30.0))
        self.use_quasi_continuous_coupling = bool(self.params.get("quasi_continuous_coupling", False))
        self.phase_tau = float(self.params.get("phase_tau", CONTINUUM_PHASE_LAG))

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        gamma_top = float(inputs.get("berry_phase_top", 0.0))
        gamma_bottom = float(inputs.get("berry_phase_bottom", 0.0))
        strain = float(inputs.get("strain_density", 1.0))
        r_coherence = float(inputs.get("coherence_r", 0.95))
        radius = float(inputs.get("radius", 1.0))
        values = (gamma_top, gamma_bottom, strain, r_coherence, radius)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("compute inputs must be finite")
        if radius <= 0:
            radius = 1e-6

        delta_gamma = gamma_top - gamma_bottom
        deficit_rad = np.radians(self.angular_deficit_deg)
        asymmetric_torque = self.kappa_torsion * delta_gamma * strain * np.sin(deficit_rad)
        pump_thrust = (1.0 - self.alpha_screening) * r_coherence * np.tanh(strain) * np.cos(delta_gamma / 2.0)
        incoherent_residual = self.compaction_density * (1.0 - self.alpha_screening) * max(0.0, 1.0 - r_coherence)
        emergent_monopole_flux = incoherent_residual / (radius ** 2)

        result = {
            "delta_gamma": delta_gamma,
            "asymmetric_torque": asymmetric_torque,
            "pump_thrust": pump_thrust,
            "incoherent_residual": incoherent_residual,
            "emergent_monopole_flux": emergent_monopole_flux,
        }
        # Opt-in only: absent from legacy output to preserve its exact interface.
        if self.use_quasi_continuous_coupling:
            dt = float(inputs.get("phase_budget_dt", SAMPLING_TICK_GAP))
            phase_scale = quasi_continuous_coupling(1.0, delta_gamma / 2.0, dt, self.phase_tau)
            result["pump_thrust"] *= phase_scale
            result.update({
                "phase_budget_scale": phase_scale,
                "continuum_phase_lag": CONTINUUM_PHASE_LAG,
                "sampling_tick_gap": SAMPLING_TICK_GAP,
                "phase_contrast_ratio": CONTRAST_RATIO,
            })
        return result
