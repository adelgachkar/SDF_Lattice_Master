"""
Phase 2 Berry Phase and Super-Critical Dynamics Engine for 5-Tetrahedron Lattice Geometry.
Implements:
  - Berry connection A(R) and curvature Omega(R) for 5-tetrahedron ring geometry
  - Geometric phase tracking: Forward (gamma_+) and Backward (gamma_-)
  - Geometric phase leak rate: Gamma_leak(Delta_gamma) = Gamma_0 * sinh(|Delta_gamma| / gamma_c)
  - Super-critical Blandford-Znajek equivalent chiral polar jet emission (P_drive > P_crit)
  - Kinetic stability locking verification: d(Delta_omega)/dt -> 0 & Lyapunov stability
"""

import numpy as np
from typing import Dict, Any, Tuple
from sdf_lattice.nodes.base import Node


class BerryDynamicsNode(Node):
    """
    Computes Berry connections, forward/backward geometric phases, curvature tensor,
    phase leakage rate, and Blandford-Znajek chiral polar jet emission for 5-tetrahedron cavity.
    """
    type_name = "berry_dynamics"

    def __init__(self, node_id: str, params: Dict[str, Any] = None):
        super().__init__(node_id, params)
        # 5-Tetrahedron geometric & physical constants
        self.N = int(self.params.get("num_tetrahedra", 5))
        self.angular_deficit_deg = float(self.params.get("angular_deficit_deg", 7.36))
        self.angular_deficit_rad = np.deg2rad(self.angular_deficit_deg)
        self.alpha_inv = float(self.params.get("alpha_inv", 137.036))
        self.P_crit = float(self.params.get("P_crit", 0.85))  # Super-critical threshold
        self.gamma_c = float(self.params.get("gamma_c", 0.45)) # Critical geometric phase scale
        self.Gamma_0 = float(self.params.get("Gamma_0", 0.05)) # Baseline phase leak rate
        self.BZ_efficiency = float(self.params.get("BZ_efficiency", 0.62)) # Blandford-Znajek jet coupling
        self.spin_parameter = float(self.params.get("spin_parameter", 0.94)) # Cavity effective spin a*

    def compute_berry_connection_and_curvature(self, R_vectors: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates Berry connection A_i and Berry curvature Omega_ij over the parameter loop R(t).
        R_vectors shape: (M, 3) or (N, 3) representing trajectory in geometric parameter space.
        For 5-tetrahedron angular deficit manifold:
        Omega_z = (angular_deficit) / (2 * Area_loop)
        """
        # Discrete geometric circulation
        diffs = np.diff(R_vectors, axis=0)
        # Connection A_k = sum_l eps_klm R_m / |R|^3 or vortex gauge
        norms = np.linalg.norm(R_vectors, axis=-1, keepdims=True) + 1e-12
        A = np.cross(np.array([0, 0, 1.0]), R_vectors) / (2.0 * norms**2)
        
        # Curvature integral ~ solid angle subtended
        # For 5-tetrahedron ring, net curvature flux equals angular deficit
        Omega = self.angular_deficit_rad * (R_vectors / norms)
        return A, Omega

    def compute_geometric_phases(self, phases: np.ndarray, coupling_matrix: np.ndarray) -> Dict[str, float]:
        """
        Computes forward (gamma_+) and backward (gamma_-) geometric Berry phases
        along the cyclic 5-tetrahedron ring.
        phases: 1D array of shape (N,) representing tetrahedron oscillator phases
        """
        N = len(phases)
        # Forward circulation: sum along + cycle (0->1->2->3->4->0)
        dphi_fwd = np.zeros(N)
        for i in range(N):
            next_i = (i + 1) % N
            dphi_fwd[i] = np.sin(phases[next_i] - phases[i])
        
        # Backward circulation: sum along - cycle (0->4->3->2->1->0)
        dphi_bwd = np.zeros(N)
        for i in range(N):
            prev_i = (i - 1) % N
            dphi_bwd[i] = np.sin(phases[prev_i] - phases[i])

        # Topological chiral factor from 5-fold deficit
        chiral_factor = (1.0 + self.angular_deficit_rad / (2 * np.pi))
        gamma_plus = np.sum(dphi_fwd) * chiral_factor / N
        gamma_minus = np.sum(dphi_bwd) * (1.0 / chiral_factor) / N
        
        delta_gamma = gamma_plus - gamma_minus
        
        # Phase leak rate: Gamma_leak = Gamma_0 * sinh(|delta_gamma| / gamma_c)
        gamma_leak = self.Gamma_0 * np.sinh(np.abs(delta_gamma) / self.gamma_c)
        
        return {
            "gamma_plus": float(gamma_plus),
            "gamma_minus": float(gamma_minus),
            "delta_gamma": float(delta_gamma),
            "gamma_leak": float(gamma_leak)
        }

    def compute_supercritical_blandford_znajek_jets(self, P_drive: float, delta_gamma: float, omega_mean: float) -> Dict[str, float]:
        """
        Super-critical Blandford-Znajek equivalent chiral polar jet emission when P_drive > P_crit.
        P_jet = BZ_efficiency * (a*)^2 * (P_drive - P_crit)^+ * (omega_mean)^2 * (1 +- chiral_asymmetry)
        """
        if P_drive > self.P_crit:
            overdrive = P_drive - self.P_crit
            # Base jet power
            P_base = self.BZ_efficiency * (self.spin_parameter**2) * overdrive * (omega_mean**2)
            # Chiral split based on Berry phase asymmetry delta_gamma
            chiral_bias = np.tanh(delta_gamma / self.gamma_c)
            jet_north = P_base * (1.0 + chiral_bias) * 0.5
            jet_south = P_base * (1.0 - chiral_bias) * 0.5
            jet_total = jet_north + jet_south
            supercritical_state = True
        else:
            jet_north = 0.0
            jet_south = 0.0
            jet_total = 0.0
            supercritical_state = False

        return {
            "jet_north": float(jet_north),
            "jet_south": float(jet_south),
            "jet_total": float(jet_total),
            "supercritical_state": supercritical_state,
            "chiral_asymmetry_ratio": float((jet_north - jet_south) / (jet_total + 1e-12))
        }

    def verify_kinetic_stability_locking(self, omega_history: np.ndarray, window: int = 50) -> Dict[str, Any]:
        """
        Verifies kinetic stability locking:
        1. Frequency spread variance: Var(Delta_omega) -> 0
        2. Lyapunov exponent proxy lambda = (1/T) * ln(|Delta(T)| / |Delta(0)|) < 0
        """
        if len(omega_history) < window:
            return {"locked": False, "lyapunov_exponent": 0.0, "frequency_variance": 1.0}
        
        recent_omega = omega_history[-window:]
        omega_spread = np.std(recent_omega, axis=1) # std across the 5 tetrahedra
        mean_var = np.mean(omega_spread**2)
        
        # Lyapunov exponent estimation across time window
        delta_0 = omega_spread[0] + 1e-12
        delta_T = omega_spread[-1] + 1e-12
        lyapunov = (1.0 / window) * np.log(delta_T / delta_0)
        
        is_locked = bool((lyapunov < 0.0 or mean_var < 1e-4) and mean_var < 0.05)
        
        return {
            "locked": is_locked,
            "lyapunov_exponent": float(lyapunov),
            "frequency_variance": float(mean_var),
            "stability_margin": float(np.exp(-abs(lyapunov)))
        }

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard SDF Lattice node compute implementation.
        """
        phases = np.asarray(inputs.get("phases", np.zeros(self.N)))
        omega = np.asarray(inputs.get("omega", np.ones(self.N)))
        P_drive = float(inputs.get("P_drive", 0.95))
        omega_history = np.asarray(inputs.get("omega_history", omega.reshape(1, -1)))
        
        geo_phases = self.compute_geometric_phases(phases, np.eye(self.N))
        bz_jets = self.compute_supercritical_blandford_znajek_jets(
            P_drive=P_drive,
            delta_gamma=geo_phases["delta_gamma"],
            omega_mean=float(np.mean(omega))
        )
        stability = self.verify_kinetic_stability_locking(omega_history)
        
        return {
            "geometric_phases": geo_phases,
            "blandford_znajek_jets": bz_jets,
            "kinetic_stability": stability,
            "node_status": "SUPER_CRITICAL_LOCKED" if (bz_jets["supercritical_state"] and stability["locked"]) else "ACTIVE"
        }
