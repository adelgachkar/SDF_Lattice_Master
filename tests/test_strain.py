import math
import unittest

from sdf_lattice.nodes.strain import StrainTensorNode


class TestStrainTensorNode(unittest.TestCase):
    def test_identity_tensor(self):
        node = StrainTensorNode("s1", {"critical_threshold": 0.5})
        res = node.compute({"tensor": [[1.0, 0.0], [0.0, 1.0]]})
        self.assertAlmostEqual(res["trace"], 2.0)
        self.assertAlmostEqual(res["hydrostatic"], 1.0)
        self.assertEqual(res["deviatoric"], [[0.0, 0.0], [0.0, 0.0]])
        self.assertAlmostEqual(res["frobenius_dev"], 0.0)
        self.assertFalse(res["is_critical"])

    def test_pure_shear_critical(self):
        node = StrainTensorNode("s2", {"critical_threshold": 1.0})
        res = node.compute({"tensor": [[0.0, 1.0], [1.0, 0.0]]})
        self.assertAlmostEqual(res["frobenius_dev"], math.sqrt(2.0))
        self.assertTrue(res["is_critical"])

    def test_general_3d_decomposition(self):
        res = StrainTensorNode("s3").compute({"tensor": [[2, 0, 0], [0, 1, 0], [0, 0, 0]]})
        self.assertAlmostEqual(res["trace"], 3.0)
        self.assertAlmostEqual(res["hydrostatic"], 1.0)
        self.assertEqual(res["deviatoric"], [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, -1.0]])
        self.assertAlmostEqual(res["frobenius_dev"], math.sqrt(2))

    def test_threshold_is_inclusive(self):
        res = StrainTensorNode("s", {"critical_threshold": math.sqrt(2)}).compute(
            {"tensor": [[0, 1], [1, 0]]})
        self.assertTrue(res["is_critical"])

    def test_missing_tensor(self):
        with self.assertRaises(KeyError):
            StrainTensorNode("s").compute({})

    def test_invalid_shapes(self):
        node = StrainTensorNode("s")
        for tensor in ([], [[1, 2]], [[1], [2]], "12"):
            with self.subTest(tensor=tensor), self.assertRaises(ValueError):
                node.compute({"tensor": tensor})

    def test_asymmetric_tensor_error(self):
        with self.assertRaises(ValueError):
            StrainTensorNode("s").compute({"tensor": [[1.0, 2.0], [0.0, 1.0]]})

    def test_rejects_nonfinite_and_non_numeric_entries(self):
        node = StrainTensorNode("s")
        for tensor in ([[float("nan")]], [[float("inf")]], [["1"]], [[True]]):
            with self.subTest(tensor=tensor), self.assertRaises(ValueError):
                node.compute({"tensor": tensor})

    def test_threshold_validation(self):
        for threshold in (-1, float("nan"), float("inf"), "bad"):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                StrainTensorNode("s", {"critical_threshold": threshold})


if __name__ == "__main__":
    unittest.main()
