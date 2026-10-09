"""Berry torque and gap stress coupling node.

This node computes a phenomenological axial torque and effective gap stress
from Berry curvature and a phase imbalance or phase-rate proxy. The coupling
is phenomenological and serves as an exploratory extension, not a first-principles
derivation.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Sequence

from sdf_lattice.nodes.base import Node


def _validate_finite_float(val: Any, name: str) -> float:
    """Validate that val is a real finite float, rejecting bools and strings."""
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"{name} must be a numeric value, got {type(val).__name__}")
    f_val = float(val)
    if math.isnan(f_val) or math.isinf(f_val):
        raise ValueError(f"{name} must be a finite number, got {f_val}")
    return f_val


def _validate_vector_3d(vec: Any, name: str) -> list[float]:
    """Validate that vec is a 3D sequence of real finite floats."""
    if not isinstance(vec, Sequence) or isinstance(vec, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of 3 numbers")
    if len(vec) != 3:
        raise ValueError(f"{name} must have length 3")
    return [_validate_finite_float(x, f"{name} element") for x in vec]


class BerryTorqueNode(Node):
    """Computes Berry-curvature-induced torque and gap stress."""

    type_name = "berry_torque"

    def __init__(
        self,
        node_id: str = "berry_torque",
        params: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, params=params)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if "berry_curvature" not in inputs:
            raise ValueError("berry_curvature is required")
        curv_raw = inputs["berry_curvature"]
        if curv_raw is None:
            raise ValueError("berry_curvature cannot be None")
        curv_vec = _validate_vector_3d(curv_raw, "berry_curvature")

        has_pr = "phase_rate" in inputs and inputs["phase_rate"] is not None
        has_pi = "phase_imbalance" in inputs and inputs["phase_imbalance"] is not None

        if not has_pr and not has_pi:
            raise ValueError("Either phase_rate or phase_imbalance must be provided")
        if has_pr and has_pi:
            raise ValueError("Provide either phase_rate or phase_imbalance, not both")

        scale_val = inputs.get("phase_rate_scale", 1.0)
        phase_rate_scale = _validate_finite_float(scale_val, "phase_rate_scale")

        if has_pr:
            raw_rate = inputs["phase_rate"]
            phase_drive_rate = _validate_finite_float(raw_rate, "phase_rate") * phase_rate_scale
            drive_source = "phase_rate"
        else:
            raw_imbalance = inputs["phase_imbalance"]
            phase_drive_rate = _validate_finite_float(raw_imbalance, "phase_imbalance") * phase_rate_scale
            drive_source = "phase_imbalance"

        coeff_val = inputs.get("coupling_coefficient", 1.0)
        coupling_coeff = _validate_finite_float(coeff_val, "coupling_coefficient")

        lever_raw = inputs.get("lever_arm", 1.0)
        lever_arm = _validate_finite_float(lever_raw, "lever_arm")
        if lever_arm <= 0.0:
            raise ValueError("lever_arm must be positive")

        if "gap_area" not in inputs or inputs["gap_area"] is None:
            raise ValueError("gap_area is required and cannot be None")
        gap_area = _validate_finite_float(inputs["gap_area"], "gap_area")
        if gap_area <= 0.0:
            raise ValueError("gap_area must be positive")

        norm_raw = inputs.get("gap_normal", [0.0, 0.0, 1.0])
        norm_vec = _validate_vector_3d(norm_raw, "gap_normal")
        norm_mag = math.sqrt(sum(x * x for x in norm_vec))
        if norm_mag == 0.0:
            raise ValueError("gap_normal cannot be zero vector")
        unit_normal = [x / norm_mag for x in norm_vec]

        # Torque T = kappa * q * Omega
        torque = [coupling_coeff * phase_drive_rate * c for c in curv_vec]
        torque_mag = math.sqrt(sum(t * t for t in torque))

        # Project torque onto gap normal
        normal_torque = sum(t * n for t, n in zip(torque, unit_normal))

        # Gap stress = normal_torque / (gap_area * lever_arm)
        gap_stress = normal_torque / (gap_area * lever_arm)

        return {
            "torque_vector": torque,
            "torque_magnitude": torque_mag,
            "normal_torque": normal_torque,
            "gap_stress": gap_stress,
            "gap_normal_unit": unit_normal,
            "drive_source": drive_source,
            "effective_drive": phase_drive_rate,
            "phase_drive_rate": phase_drive_rate,
            "coupling_coefficient": coupling_coeff,
            "phenomenological": True,
        }
