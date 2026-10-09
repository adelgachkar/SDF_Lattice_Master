"""Node for evaluating Pre-Friedmann closure constraints and lattice stability."""

from typing import Any, Dict, List, Optional
import numpy as np

from .base import Node


class ClosureConstraintsNode(Node):
    """Evaluates causal residuals, reactive energy deficits, and phase bifurcation."""

    def __init__(
        self,
        name: str = "closure_constraints",
        params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name)
        params = params or {}
        self.causality_threshold: float = float(params.get("causality_threshold", 1.50))
        self.energy_threshold: float = float(params.get("energy_threshold", 0.50))
        self.min_coherence_threshold: float = float(params.get("min_coherence_threshold", 0.20))

    @property
    def required_inputs(self) -> List[str]:
        return ["strain_tensor", "permittivity_envelope", "coupling_strength"]

    @property
    def output_keys(self) -> List[str]:
        return [
            "causality_residual",
            "energy_deficit",
            "closure_status",
            "is_stable",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        strain_raw = inputs.get(
            "strain_tensor",
            inputs.get("strain", inputs.get("strain_matrix", 0.0)),
        )
        eps_raw = inputs.get(
            "permittivity_envelope",
            inputs.get("permittivity", inputs.get("envelope", 1.0)),
        )
        coupling_raw = inputs.get(
            "coupling_strength",
            inputs.get("coupling", inputs.get("g_coupling", 1.0)),
        )
        # Optional coherence input from VoidCouplingNode
        phase_coherence = inputs.get(
            "phase_coherence",
            inputs.get("coherence", None),
        )

        strain = np.asarray(strain_raw, dtype=float)
        epsilon = np.asarray(eps_raw, dtype=float)
        g_coupling = float(coupling_raw)

        strain_norm = float(np.mean(strain**2)) if strain.size > 0 else 0.0
        envelope_dispersion = float(np.var(epsilon)) if epsilon.size > 0 else 0.0
        mean_eps = float(np.mean(epsilon)) if epsilon.size > 0 else 1.0

        # Causality residual & Energy deficit
        causality_residual = abs(strain_norm - (g_coupling * mean_eps) - envelope_dispersion)
        energy_deficit = abs(1.0 - (mean_eps * (1.0 + 0.1 * strain_norm)))

        # Coherence stability check
        coherence_stable = True
        if phase_coherence is not None:
            coherence_stable = float(phase_coherence) >= self.min_coherence_threshold

        # Primary stability condition
        causal_stable = causality_residual < self.causality_threshold
        energy_stable = energy_deficit < self.energy_threshold

        is_stable = causal_stable and energy_stable and coherence_stable

        # Determine closure status
        if not coherence_stable or (not causal_stable and not energy_stable):
            closure_status = "BIFURCATION_COLLAPSE"
        elif not causal_stable and energy_stable:
            closure_status = "PHASE_LEAKAGE"
        elif causal_stable and not energy_stable:
            closure_status = "ENERGY_DIVERGENCE"
        else:
            closure_status = "BOUND_STABLE"

        return {
            "causality_residual": causality_residual,
            "energy_deficit": energy_deficit,
            "closure_status": closure_status,
            "is_stable": is_stable,
        }
