"""Legacy and phase-budget regression tests for PeristalticPumpNode."""
import math
import unittest
from sdf_lattice.nodes.peristaltic_pump import (
    PeristalticPumpNode, CONTINUUM_PHASE_LAG, SAMPLING_TICK_GAP,
    CONTRAST_RATIO, quasi_continuous_coupling,
)


class TestPeristalticPumpNode(unittest.TestCase):
    def setUp(self):
        self.params = {"angular_deficit_deg": 7.36, "kappa_torsion": 1.37,
                       "compaction_density": 5.0, "alpha_screening": 2.0 / 30.0}
        self.node = PeristalticPumpNode("pump_1", self.params)

    def test_monopole_inverse_square_and_legacy_interface(self):
        inputs = {"berry_phase_top": 0.5, "berry_phase_bottom": 0.1,
                  "strain_density": 1.2, "coherence_r": 0.80, "radius": 2.0}
        res = self.node.compute(inputs)
        self.assertEqual(set(res), {"delta_gamma", "asymmetric_torque", "pump_thrust",
                                    "incoherent_residual", "emergent_monopole_flux"})
        self.assertAlmostEqual(res["delta_gamma"], 0.4, places=5)
        self.assertGreater(res["asymmetric_torque"], 0.0)
        self.assertGreater(res["pump_thrust"], 0.0)
        self.assertGreater(res["incoherent_residual"], 0.0)
        self.assertAlmostEqual(res["emergent_monopole_flux"], res["incoherent_residual"] / 4.0, places=5)

    def test_full_incoherence_gravity(self):
        res = self.node.compute({"berry_phase_top": 0.0, "berry_phase_bottom": 0.0,
                                 "strain_density": 1.0, "coherence_r": 0.0, "radius": 1.0})
        expected = 5.0 * (1.0 - 2.0 / 30.0)
        self.assertAlmostEqual(res["incoherent_residual"], expected, places=4)
        self.assertAlmostEqual(res["emergent_monopole_flux"], expected, places=4)

    def test_optional_phase_budgeting(self):
        node = PeristalticPumpNode("pump_smooth", {**self.params, "quasi_continuous_coupling": True})
        values = {"berry_phase_top": 0.6, "berry_phase_bottom": 0.2, "strain_density": 1.2,
                  "coherence_r": 0.8, "phase_budget_dt": SAMPLING_TICK_GAP}
        legacy = self.node.compute(values)
        smooth = node.compute(values)
        expected_scale = -math.expm1(-SAMPLING_TICK_GAP / CONTINUUM_PHASE_LAG) * math.cos((0.6 - 0.2) / 2.0)
        self.assertAlmostEqual(smooth["phase_budget_scale"], expected_scale)
        self.assertAlmostEqual(smooth["pump_thrust"], legacy["pump_thrust"] * expected_scale)
        self.assertEqual(smooth["continuum_phase_lag"], 0.032)
        self.assertEqual(smooth["sampling_tick_gap"], 0.004)
        self.assertEqual(smooth["phase_contrast_ratio"], 8.0)
        self.assertAlmostEqual(CONTRAST_RATIO, 8.0)

    def test_compute_rejects_non_finite_inputs(self):
        for key in ("berry_phase_top", "berry_phase_bottom", "strain_density", "coherence_r", "radius"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(key=key, value=value):
                    with self.assertRaises(ValueError):
                        self.node.compute({key: value})

    def test_phase_coupling_zero_time_and_zero_relaxation(self):
        self.assertEqual(quasi_continuous_coupling(2.0, 0.0, 0.0), 0.0)
        self.assertAlmostEqual(quasi_continuous_coupling(2.0, 0.0, 1.0, 0.0), 2.0)


if __name__ == "__main__": unittest.main()
