"""Harmonic cavity resilience and volume stabilization node."""
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Dict

from .base import Node


class CavityResilienceNode(Node):
    """
    Cavity Volume Resilience and Dynamic Pressure Feedback Node.

    Models the stabilization of vacuum foam / cavity cells via internal
    harmonic vacuum pressure, boundary wall elasticity (effective Archimedean
    restoring stress), and Berry connection contributions. Prevents unconstrained
    runaway inflation or catastrophic void collapse.

    Governing Balance:
        P_net = P_harmonic + P_elastic + P_berry - P_inflation
        dV/dt = kappa_v * P_net - gamma_v * (V - V0)
    """

    type_name = "cavity_resilience"
    NODE_TYPE = "cavity_resilience"

    def __init__(self, node_id: str, params: Dict[str, Any] | None = None):
        super().__init__(node_id, params)
        self.v0 = self._parameter("v0", 1.0)
        self.r_wall = self._parameter("r_wall", 0.85)
        self.k_elastic = self._parameter("k_elastic", 1.2)
        self.gamma_v = self._parameter("gamma_v", 0.1)
        self.kappa_v = self._parameter("kappa_v", 0.05)
        self.dt = self._parameter("dt", 0.01)

        if self.v0 <= 0.0:
            raise ValueError("v0 (equilibrium volume) must be strictly positive")
        if not (0.0 <= self.r_wall <= 1.0):
            raise ValueError("r_wall (wall reflection coefficient) must be in [0, 1]")
        if self.k_elastic < 0.0:
            raise ValueError("k_elastic must be non-negative")
        if self.gamma_v < 0.0:
            raise ValueError("gamma_v (damping rate) must be non-negative")
        if self.kappa_v <= 0.0:
            raise ValueError("kappa_v (response mobility) must be strictly positive")
        if self.dt <= 0.0:
            raise ValueError("dt (time step) must be strictly positive")

    def _parameter(self, name: str, default: float) -> float:
        value = self.params.get(name, default)
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"Parameter '{name}' must be a finite real number")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f"Parameter '{name}' must be a finite real number")
        return result

    @staticmethod
    def _number(value: Any, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"Input '{name}' must be a finite real number")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f"Input '{name}' must be a finite real number")
        return result

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute stabilized volume, dynamic net pressure, and boundary strain.

        Expected input ports:
            - current_volume (float, optional, default: v0): current cavity volume V
            - p_harmonic (float, optional, default: 0.0): internal Casimir harmonic pressure
            - p_berry (float, optional, default: 0.0): Berry phase-induced geometric torque/pressure
            - p_inflation (float, optional, default: 0.0): cosmological/regional inflation expansion pressure
            - dynamic_r_wall (float, optional): dynamic wall reflection coefficient override
        """
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a mapping")

        current_v = self._number(inputs.get("current_volume", self.v0), "current_volume")
        if current_v <= 0.0:
            raise ValueError("current_volume must be strictly positive")

        p_harmonic = self._number(inputs.get("p_harmonic", 0.0), "p_harmonic")
        p_berry = self._number(inputs.get("p_berry", 0.0), "p_berry")
        p_inflation = self._number(inputs.get("p_inflation", 0.0), "p_inflation")

        # Dynamic wall reflection coefficient if modulated by regional strain
        if "dynamic_r_wall" in inputs:
            r_wall = self._number(inputs["dynamic_r_wall"], "dynamic_r_wall")
            if not (0.0 <= r_wall <= 1.0):
                raise ValueError("dynamic_r_wall must be in [0, 1]")
        else:
            r_wall = self.r_wall

        # Elastic Archimedean boundary restoring pressure:
        # P_elastic = - k_elastic * r_wall * ((V - V0) / V0)
        vol_deviation = (current_v - self.v0) / self.v0
        p_elastic = -self.k_elastic * r_wall * vol_deviation

        # Net boundary driving pressure
        p_net = p_harmonic + p_elastic + p_berry - p_inflation

        # Dynamic Volume Evolution: dV/dt = kappa_v * p_net - gamma_v * (current_v - v0)
        dv_dt = (self.kappa_v * p_net) - (self.gamma_v * (current_v - self.v0))
        updated_v = current_v + (dv_dt * self.dt)

        # Physical safety clamp: volume must not collapse to non-positive
        min_cutoff = 1e-6 * self.v0
        if updated_v < min_cutoff:
            updated_v = min_cutoff

        # Boundary volumetric strain
        volumetric_strain = (updated_v - self.v0) / self.v0
        is_stable = abs(dv_dt) < 1e-4

        return {
            "volume": updated_v,
            "dv_dt": dv_dt,
            "p_net": p_net,
            "p_elastic": p_elastic,
            "volumetric_strain": volumetric_strain,
            "is_stable": is_stable,
        }
