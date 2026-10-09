"""Strain Tensor Node implementation with full decomposition."""

from typing import Any, Dict, List, Optional
import numpy as np
from .base import Node

class StrainTensorNode(Node):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name)
        self.config = config or {}
        val = self.config.get("critical_threshold", 1.0)
        
        # Strict validation for the stability threshold
        if not isinstance(val, (int, float)) or not np.isfinite(val) or val <= 0:
            raise ValueError("Invalid critical_threshold")
            
        self.critical_threshold = val

    @property
    def required_inputs(self) -> List[str]:
        return ["tensor"]

    @property
    def provided_outputs(self) -> List[str]:
        return ["strain_tensor", "trace", "hydrostatic", "deviatoric", "frobenius_dev", "is_critical"]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Explicit key-presence checks
        if "tensor" in inputs:
            raw_data = inputs["tensor"]
        elif "displacement_gradient" in inputs:
            raw_data = inputs["displacement_gradient"]
        else:
            raise KeyError("Input 'tensor' or 'displacement_gradient' is required")

        try:
            data = np.asarray(raw_data, dtype=float)
        except (ValueError, TypeError):
            raise ValueError("Input must be numeric")

        # Shape checks (2x2 and 3x3 supported)
        if data.shape not in [(2, 2), (3, 3)]:
            raise ValueError("Input must be a 2x2 or 3x3 matrix")
        
        if not np.all(np.isfinite(data)):
            raise ValueError("Input must contain only finite numbers")

        if not np.allclose(data, data.T):
            raise ValueError("Strain tensor must be symmetric")

        # Main computation
        strain = 0.5 * (data + data.T)
        trace_val = np.trace(strain)
        dim = data.shape[0]
        
        # Hydrostatic part
        hydrostatic = trace_val / dim
        
        # Deviatoric tensor
        deviatoric = strain - (hydrostatic * np.eye(dim))
        
        # Frobenius norm of the deviatoric tensor
        frobenius_dev = np.linalg.norm(deviatoric, ord='fro')
        
        # Critical-state check
        is_critical = bool(frobenius_dev >= self.critical_threshold)

        result = {
            "strain_tensor": strain.tolist(),
            "trace": float(trace_val),
            "hydrostatic": float(hydrostatic),
            "deviatoric": deviatoric.tolist(),
            "frobenius_dev": float(frobenius_dev),
            "is_critical": is_critical
        }
        # Strain remains dimensionless and is never reinterpreted as stress.
        # Stress outputs are emitted only when an explicit Berry stress is supplied.
        if "berry_gap_stress" in inputs or "berry_torque_result" in inputs:
            raw_berry = inputs.get("berry_gap_stress")
            if raw_berry is None:
                raw_berry = inputs["berry_torque_result"]
                if not isinstance(raw_berry, dict) or "gap_stress" not in raw_berry:
                    raise ValueError("berry_torque_result must contain gap_stress")
                raw_berry = raw_berry["gap_stress"]
            berry_stress = self._stress_scalar(raw_berry, "berry_gap_stress")
            baseline = self._stress_scalar(inputs.get("base_gap_stress", 0.0), "base_gap_stress")
            effective = baseline + berry_stress
            if not np.isfinite(effective):
                raise ValueError("effective_gap_stress must be finite")
            result["berry_gap_stress"] = berry_stress
            result["effective_gap_stress"] = float(effective)
        return result

    @staticmethod
    def _stress_scalar(value: Any, name: str) -> float:
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.number)):
            raise ValueError(f"{name} must be a finite numeric value")
        result = float(value)
        if not np.isfinite(result):
            raise ValueError(f"{name} must be a finite numeric value")
        return result
