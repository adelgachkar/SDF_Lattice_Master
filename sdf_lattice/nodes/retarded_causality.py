"""
Retarded Causality Guard Node with Adiabatic Phase Budgeting (v0.3.3)
Enforces lightcone bounds and eliminates Gibbs phenomena via 8:1 phase continuum relaxation.
"""

from typing import Any, Dict, Optional
import math
from .base import Node

# Core Phase Budgeting Constants (Continuum Ratio 8.0)
CONTINUUM_PHASE_LAG: float = 0.032
SAMPLING_TICK_GAP: float = 0.004
CONTRAST_RATIO: float = CONTINUUM_PHASE_LAG / SAMPLING_TICK_GAP  # Exactly 8.0
# Backward-compatible names retained for existing callers.
PHASE_CONTINUUM: float = CONTINUUM_PHASE_LAG
PHASE_SAMPLING: float = SAMPLING_TICK_GAP
DYNAMIC_CONTRAST_RATIO: float = CONTRAST_RATIO


def quasi_continuous_coupling(
    amplitude: float,
    phase: float,
    dt: float,
    tau_relax: float = PHASE_CONTINUUM,
) -> float:
    """
    Adiabatic low-pass phase relaxation filter to eliminate Gibbs ringing
    and maintain C^1 continuity across discrete simulation ticks.
    """
    if tau_relax <= 0.0:
        return amplitude * math.cos(phase)
    scaling = 1.0 - math.exp(-max(dt, 0.0) / tau_relax)
    return amplitude * scaling * math.cos(phase)


class RetardedCausalityNode(Node):
    """
    Guards causal propagation across lattice voids, ensuring signals obey v_max
    and applying smooth adiabatic filtering under retarded potential dynamics.
    """
    type_name = "retarded_causality"

    def __init__(self, node_id: str, params: Optional[Dict[str, Any]] = None, **kwargs):
        # Support both 'params' and 'config' keyword arguments transparently
        cfg = params if params is not None else kwargs.get("config", {})
        super().__init__(node_id, cfg)
        self.v_max: float = max(float(self.params.get("v_max", 1.0)), 1e-12)
        self.epsilon_time: float = float(self.params.get("epsilon_time", 1e-9))
        self.strict_enforce: bool = bool(self.params.get("strict_enforce", True))
        self.damping: float = max(float(self.params.get("damping", 0.0)), 0.0)
        if not math.isfinite(self.damping):
            raise ValueError("damping must be finite")
        if not math.isfinite(self.v_max) or not math.isfinite(self.epsilon_time):
            raise ValueError("v_max and epsilon_time must be finite")

    def _arrival_time(self, distance: float, t_source: float) -> float:
        """Calculates earliest theoretical signal arrival time."""
        return t_source + (max(distance, 0.0) / self.v_max)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        distance = float(inputs.get("distance", 1.0))
        delta_t = float(inputs.get("delta_t", 0.0))
        source_signal = float(inputs.get("source_signal", 1.0))
        t_src = float(inputs.get("t_source", 0.0))
        carrier_phase = float(inputs.get("phase", 0.0))

        values = (distance, delta_t, source_signal, t_src, carrier_phase)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("compute inputs must be finite")
        distance = max(distance, 0.0)
        t_min_arrival = self._arrival_time(distance, 0.0)
        is_spacelike = (delta_t + self.epsilon_time) < t_min_arrival

        if is_spacelike and self.strict_enforce:
            received_signal = 0.0
            blocked = True
            causality_violation = False
        elif is_spacelike and not self.strict_enforce:
            received_signal = source_signal
            blocked = False
            causality_violation = True
        else:
            dt_effective = max(delta_t - t_min_arrival, PHASE_SAMPLING)
            received_signal = quasi_continuous_coupling(
                amplitude=source_signal,
                phase=carrier_phase,
                dt=dt_effective,
                tau_relax=PHASE_CONTINUUM,
            ) * math.exp(-self.damping * max(distance, 0.0))
            blocked = False
            causality_violation = False

        return {
            "node_id": self.node_id,
            "distance": distance,
            "delta_t": delta_t,
            "t_min_arrival": t_min_arrival,
            "is_spacelike": is_spacelike,
            "received_signal": received_signal,
            "blocked": blocked,
            "causality_violation": causality_violation,
            "contrast_ratio": DYNAMIC_CONTRAST_RATIO,
        }
