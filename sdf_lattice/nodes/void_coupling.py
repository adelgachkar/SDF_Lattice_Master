"""Five-edge phase coupling and cavity circulation node."""
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Dict

from .base import Node


class VoidCouplingNode(Node):
    """Compute phase coherence, bridge phase, coupling energy and ring flux."""

    type_name = "void_coupling"

    def __init__(self, node_id: str, params: Dict[str, Any] | None = None):
        super().__init__(node_id, params)
        self.coupling_constant = self._parameter("coupling_constant", 1.0)
        self.critical_coherence_threshold = self._parameter("critical_coherence_threshold", 0.7)
        self.bridge_phase_offset = self._parameter("bridge_phase_offset", 0.0)
        if self.coupling_constant <= 0:
            raise ValueError("coupling_constant must be finite and greater than zero")
        if not 0.0 <= self.critical_coherence_threshold <= 1.0:
            raise ValueError("critical_coherence_threshold must be between zero and one")

    def _parameter(self, name: str, default: float) -> float:
        value = self.params.get(name, default)
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real number")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite real number")
        return result

    @staticmethod
    def _number(value: Any, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real number")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite real number")
        return result

    @classmethod
    def _circulation(cls, samples: Any) -> float:
        if samples is None:
            return 0.0
        if isinstance(samples, (str, bytes)):
            raise ValueError("vector_potential_samples must be a sequence")
        try:
            samples = list(samples)
        except TypeError as exc:
            raise ValueError("vector_potential_samples must be a sequence") from exc
        terms = []
        for index, sample in enumerate(samples):
            if isinstance(sample, (tuple, list)):
                if len(sample) != 2:
                    raise ValueError(f"vector potential sample {index} must be (A, dl)")
                a = cls._number(sample[0], f"vector_potential_samples[{index}].A")
                dl = cls._number(sample[1], f"vector_potential_samples[{index}].dl")
                terms.append(a * dl)
            else:
                terms.append(cls._number(sample, f"vector_potential_samples[{index}]"))
        flux = math.fsum(terms)
        if not math.isfinite(flux):
            raise ValueError("computed cavity_flux must be finite")
        return flux

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a mapping")
        if "edge_phases" not in inputs:
            raise KeyError("Input 'edge_phases' is required")
        raw_phases = inputs["edge_phases"]
        if isinstance(raw_phases, (str, bytes)):
            raise ValueError("edge_phases must contain exactly five real numbers")
        try:
            raw_phases = list(raw_phases)
        except TypeError as exc:
            raise ValueError("edge_phases must contain exactly five real numbers") from exc
        if len(raw_phases) != 5:
            raise ValueError("edge_phases must contain exactly five real numbers")
        phases = [self._number(x, f"edge_phases[{i}]") for i, x in enumerate(raw_phases)]

        radiative_flux = self._number(inputs.get("radiative_flux", 0.0), "radiative_flux")
        if radiative_flux < 0:
            raise ValueError("radiative_flux must be non-negative")
        cosines = [math.cos(theta) for theta in phases]
        sines = [math.sin(theta) for theta in phases]
        re = math.fsum(cosines) / 5.0
        im = math.fsum(sines) / 5.0
        coherence = math.hypot(re, im)
        # Avoid tiny floating excursions outside the mathematical range [0, 1].
        coherence = min(1.0, max(0.0, coherence))
        mean_phase = math.atan2(im, re) if coherence > 1e-15 else 0.0
        bridge_phase = (mean_phase + self.bridge_phase_offset) % (2.0 * math.pi)
        coupling_energy = 0.5 * self.coupling_constant * coherence**2 * (1.0 + radiative_flux)
        if not math.isfinite(coupling_energy):
            raise ValueError("computed coupling_energy must be finite")
        matrix = [[math.cos(phases[j] - phases[k]) for k in range(5)] for j in range(5)]
        return {
            "phase_coherence": coherence,
            "mean_phase": mean_phase,
            "bridge_phase": bridge_phase,
            "coupling_energy": coupling_energy,
            "cavity_flux": self._circulation(inputs.get("vector_potential_samples")),
            "is_phase_locked": coherence >= self.critical_coherence_threshold,
            "coupling_matrix": matrix,
        }
