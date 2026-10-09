import math
import unittest

from sdf_lattice.nodes.berry_torque import BerryTorqueNode
from sdf_lattice.nodes.strain import StrainTensorNode


class BerryTorqueTests(unittest.TestCase):
    def setUp(self):
        self.node = BerryTorqueNode("bt")
        self.inputs = {"berry_curvature": [0, 0, 2], "phase_rate": 3,
                       "gap_normal": [0, 0, 5], "lever_arm": 2,
                       "coupling_coefficient": 4, "gap_area": 2}

    def test_torque_vector_normal_projection_and_stress(self):
        res = self.node.compute(self.inputs)
        self.assertEqual(res["torque_vector"], [0.0, 0.0, 24.0])
        self.assertEqual(res["normal_torque"], 24.0)
        self.assertEqual(res["gap_stress"], 6.0)
        self.assertEqual(res["gap_normal_unit"], [0.0, 0.0, 1.0])

    def test_phase_imbalance_path_and_sign(self):
        values = dict(self.inputs)
        values.pop("phase_rate")
        values.update(phase_imbalance=-0.5, phase_rate_scale=2)
        res = self.node.compute(values)
        self.assertEqual(res["phase_drive_rate"], -1.0)
        self.assertEqual(res["normal_torque"], -8.0)

    def test_invalid_nonfinite_and_bool_inputs(self):
        for key, val in (("phase_rate", True), ("phase_rate", float("nan")),
                         ("berry_curvature", [0, float("inf"), 0]),
                         ("gap_normal", [0, 0, False]), ("lever_arm", float("inf")),
                         ("coupling_coefficient", "2"), ("gap_area", float("nan"))):
            bad = dict(self.inputs); bad[key] = val
            with self.subTest(key=key, val=val), self.assertRaises(ValueError):
                self.node.compute(bad)

    def test_zero_or_invalid_denominators_rejected(self):
        for key, val in (("gap_area", 0), ("gap_area", -1), ("lever_arm", 0),
                         ("gap_normal", [0, 0, 0])):
            bad = dict(self.inputs); bad[key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.node.compute(bad)

    def test_requires_area_and_exactly_one_phase_input(self):
        for edit in ({"gap_area": None}, {"phase_rate": None, "phase_imbalance": None}):
            bad = dict(self.inputs); bad.update(edit)
            with self.assertRaises((KeyError, ValueError)):
                self.node.compute(bad)

    def test_strain_backward_compatibility_and_additive_stress(self):
        node = StrainTensorNode("strain")
        tensor = {"tensor": [[1.0, 0.0], [0.0, -1.0]]}
        legacy = node.compute(tensor)
        expected = {"strain_tensor", "trace", "hydrostatic", "deviatoric", "frobenius_dev", "is_critical"}
        self.assertEqual(set(legacy), expected)
        same = node.compute({**tensor, "berry_gap_stress": 5.0})
        self.assertEqual({k: same[k] for k in expected}, legacy)
        self.assertEqual(same["berry_gap_stress"], 5.0)
        self.assertEqual(same["effective_gap_stress"], 5.0)
        summed = node.compute({**tensor, "berry_torque_result": {"gap_stress": -2.0},
                               "base_gap_stress": 7.0})
        self.assertEqual(summed["effective_gap_stress"], 5.0)


if __name__ == "__main__":
    unittest.main()
