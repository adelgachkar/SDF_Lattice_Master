"""Causality, damping, and phase-smoothing regression tests."""
import math
import unittest
from sdf_lattice.nodes.retarded_causality import (
    RetardedCausalityNode, quasi_continuous_coupling, PHASE_CONTINUUM,
    PHASE_SAMPLING, DYNAMIC_CONTRAST_RATIO,
)

class TestRetardedCausalityNode(unittest.TestCase):
    def setUp(self):
        self.node = RetardedCausalityNode("rc_guard_01", config={"v_max": 1.0,
            "epsilon_time": 1e-9, "strict_enforce": True, "damping": 0.0})

    def test_phase_budgeting_ratio(self):
        self.assertEqual(PHASE_CONTINUUM, 0.032)
        self.assertEqual(PHASE_SAMPLING, 0.004)
        self.assertEqual(DYNAMIC_CONTRAST_RATIO, 8.0)

    def test_quasi_continuous_coupling_adiabatic(self):
        out = quasi_continuous_coupling(1.0, 0.0, PHASE_SAMPLING, tau_relax=PHASE_CONTINUUM)
        self.assertAlmostEqual(out, 1.0 - math.exp(-PHASE_SAMPLING / PHASE_CONTINUUM), places=6)
        self.assertGreater(out, 0.0); self.assertLess(out, 1.0)
        self.assertEqual(quasi_continuous_coupling(2.0, 0.0, -1.0), 0.0)
        self.assertEqual(quasi_continuous_coupling(2.0, 0.0, 1.0, tau_relax=0.0), 2.0)

    def test_arrival_time_calculation(self):
        self.assertAlmostEqual(self.node._arrival_time(5.0, 10.0), 15.0)
        self.assertAlmostEqual(self.node._arrival_time(-5.0, 10.0), 10.0)

    def test_strict_causal_block_and_non_strict_violation(self):
        blocked = self.node.compute({"distance": 2.0, "delta_t": 1.0, "source_signal": 3.0})
        self.assertTrue(blocked["blocked"]); self.assertEqual(blocked["received_signal"], 0.0)
        permissive = RetardedCausalityNode("permissive", {"strict_enforce": False})
        out = permissive.compute({"distance": 2.0, "delta_t": 1.0, "source_signal": 3.0})
        self.assertTrue(out["causality_violation"]); self.assertEqual(out["received_signal"], 3.0)

    def test_negative_distance_is_clamped(self):
        negative = self.node.compute({"distance": -4.0, "delta_t": 0.5, "source_signal": 1.0})
        zero = self.node.compute({"distance": 0.0, "delta_t": 0.5, "source_signal": 1.0})
        self.assertEqual(negative["distance"], 0.0)
        self.assertEqual(negative["t_min_arrival"], 0.0)
        self.assertEqual(negative["received_signal"], zero["received_signal"])

    def test_non_finite_compute_inputs_rejected(self):
        for key in ("distance", "delta_t", "source_signal", "t_source", "phase"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(key=key, value=value):
                    with self.assertRaises(ValueError):
                        self.node.compute({key: value})

    def test_distance_damping(self):
        common = {"distance": 2.0, "delta_t": 2.1, "source_signal": 1.0, "phase": 0.0}
        undamped = self.node.compute(common)["received_signal"]
        damped = RetardedCausalityNode("damped", {"damping": 0.5}).compute(common)["received_signal"]
        self.assertAlmostEqual(damped, undamped * math.exp(-1.0))
        self.assertLess(damped, undamped)

if __name__ == "__main__": unittest.main()
