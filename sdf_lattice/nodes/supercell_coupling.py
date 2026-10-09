"""Node for evaluating Multi-Void Supercell inter-cavity phase coupling."""

from typing import Any, Dict, List, Optional
import numpy as np

from .base import Node


class SupercellCouplingNode(Node):
    """Computes collective phase coherence and inter-cavity energy across an array of voids."""

    def __init__(
        self,
        name: str = "supercell_coupling",
        params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name)
        params = params or {}
        self.inter_coupling_strength: float = float(params.get("inter_coupling_strength", 0.85))
        self.supercell_threshold: float = float(params.get("supercell_threshold", 0.65))

    @property
    def required_inputs(self) -> List[str]:
        return ["void_phase_matrix"]

    @property
    def output_keys(self) -> List[str]:
        return [
            "collective_coherence",
            "inter_cavity_energy",
            "supercell_locked",
            "coherence_spectrum",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        phase_matrix_raw = inputs.get(
            "void_phase_matrix",
            inputs.get("phase_matrix", inputs.get("voids_phases", None)),
        )

        if phase_matrix_raw is None:
            raise ValueError("SupercellCouplingNode requires 'void_phase_matrix' (N_voids x 5 edges).")

        phases = np.asarray(phase_matrix_raw, dtype=float)
        if phases.ndim != 2 or phases.shape[1] != 5:
            raise ValueError(f"Expected void_phase_matrix shape (N, 5), got {phases.shape}")

        num_voids = phases.shape[0]

        # 1. Coherence per individual void
        cos_mean = np.mean(np.cos(phases), axis=1)
        sin_mean = np.mean(np.sin(phases), axis=1)
        coherence_per_void = np.hypot(cos_mean, sin_mean)

        # 2. Collective global coherence across all voids
        collective_coherence = float(np.mean(coherence_per_void))

        # 3. Inter-cavity coupling matrix
        inter_energy = 0.0
        if num_voids > 1:
            for i in range(num_voids - 1):
                phase_diff = phases[i] - phases[i + 1]
                inter_energy += float(np.sum(np.cos(phase_diff)))
            inter_energy = 0.5 * self.inter_coupling_strength * (inter_energy / (num_voids - 1))
        else:
            inter_energy = float(coherence_per_void[0] ** 2)

        supercell_locked = bool(collective_coherence >= self.supercell_threshold)

        return {
            "collective_coherence": collective_coherence,
            "inter_cavity_energy": inter_energy,
            "supercell_locked": supercell_locked,
            "coherence_spectrum": coherence_per_void.tolist(),
        }
