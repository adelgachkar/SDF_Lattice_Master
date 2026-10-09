"""Permittivity envelope and radiative leakage model."""
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Dict

from .base import Node


class PermittivityEnvelopeNode(Node):
    """Compute a strain-dependent permittivity and its energy/leakage envelope.

    Model: ``effective_permittivity = epsilon_0 * (1 + coupling * trace)``;
    ``reactive_energy_density = 0.5 * effective_permittivity *
    (trace**2 + frobenius_dev**2)``. Flux is the configured fraction of that
    energy for critical states and zero otherwise. ``confinement_status`` is
    ``"radiative"`` when critical, and ``"confined"`` otherwise.
    """

    type_name = "permittivity_envelope"

    def __init__(self, node_id: str, params: Dict[str, Any] | None = None):
        super().__init__(node_id, params)
        self.epsilon_0 = self._parameter("epsilon_0", 1.0)
        self.photoelastic_coupling = self._parameter("photoelastic_coupling", 0.15)
        self.radiative_leak_rate = self._parameter("radiative_leak_rate", 0.85)
        if self.epsilon_0 <= 0:
            raise ValueError("epsilon_0 must be finite and greater than zero")
        if not 0 <= self.radiative_leak_rate <= 1:
            raise ValueError("radiative_leak_rate must be finite and between 0 and 1")

    def _parameter(self, name: str, default: float) -> float:
        value = self.params.get(name, default)
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real number")
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} must be a finite real number") from exc
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite real number")
        return result

    @staticmethod
    def _input_number(value: Any, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real number")
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{name} must be a finite real number") from exc
        if not math.isfinite(result):
            raise ValueError(f"{name} must be a finite real number")
        return result

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a mapping")
        trace_key = "trace" if "trace" in inputs else "eps_hydro"
        dev_key = "frobenius_dev" if "frobenius_dev" in inputs else "shear_norm"
        if trace_key not in inputs:
            raise KeyError("Input 'trace' (or 'eps_hydro') is required")
        if dev_key not in inputs:
            raise KeyError("Input 'frobenius_dev' (or 'shear_norm') is required")
        if "is_critical" not in inputs:
            raise KeyError("Input 'is_critical' is required")

        trace = self._input_number(inputs[trace_key], trace_key)
        dev = self._input_number(inputs[dev_key], dev_key)
        try:
            critical = bool(inputs["is_critical"])
        except (TypeError, ValueError) as exc:
            raise ValueError("is_critical must be boolean or truthy/falsy") from exc

        effective_permittivity = self.epsilon_0 * (1.0 + self.photoelastic_coupling * trace)
        reactive_energy_density = 0.5 * effective_permittivity * (trace * trace + dev * dev)
        radiative_flux = self.radiative_leak_rate * reactive_energy_density if critical else 0.0
        outputs = (effective_permittivity, reactive_energy_density, radiative_flux)
        if not all(math.isfinite(value) for value in outputs):
            raise ValueError("computed permittivity envelope values must be finite")
        return {
            "effective_permittivity": effective_permittivity,
            "reactive_energy_density": reactive_energy_density,
            "radiative_flux": radiative_flux,
            "confinement_status": "radiative" if critical else "confined",
        }
