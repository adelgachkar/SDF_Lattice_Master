import math
import unittest

from sdf_lattice import Graph
from sdf_lattice.nodes import (PermittivityEnvelopeNode, StrainTensorNode,
                               VoidCouplingNode)


class VoidCouplingTests(unittest.TestCase):
    def test_instantiation_and_defaults(self):
        node = VoidCouplingNode("v")
        self.assertEqual(node.type_name, "void_coupling")
        self.assertEqual(node.coupling_constant, 1.0)
        self.assertEqual(node.critical_coherence_threshold, 0.7)
        self.assertEqual(node.bridge_phase_offset, 0.0)
        result = node.compute({"edge_phases": [0] * 5})
        self.assertEqual(result["cavity_flux"], 0.0)

    def test_param_validation_invalid_coupling(self):
        for v in (0, -1, True, float("nan"), float("inf"), "1"):
            with self.subTest(value=v), self.assertRaises(ValueError):
                VoidCouplingNode("v", {"coupling_constant": v})

    def test_param_validation_invalid_threshold(self):
        for v in (-0.01, 1.01, True, float("nan"), "0.7"):
            with self.subTest(value=v), self.assertRaises(ValueError):
                VoidCouplingNode("v", {"critical_coherence_threshold": v})

    def test_compute_perfect_coherence(self):
        result = VoidCouplingNode("v").compute({"edge_phases": [0.4] * 5})
        self.assertAlmostEqual(result["phase_coherence"], 1.0)
        self.assertAlmostEqual(result["mean_phase"], 0.4)
        self.assertTrue(result["is_phase_locked"])

    def test_compute_destructive_coherence(self):
        phases = [2 * math.pi * k / 5 for k in range(5)]
        result = VoidCouplingNode("v").compute({"edge_phases": phases})
        self.assertAlmostEqual(result["phase_coherence"], 0.0, places=14)
        self.assertFalse(result["is_phase_locked"])

    def test_coupling_matrix_symmetry_and_diagonal(self):
        matrix = VoidCouplingNode("v").compute({"edge_phases": [0.1, 0.4, 1, 2, 3]})["coupling_matrix"]
        self.assertEqual(len(matrix), 5)
        for j in range(5):
            self.assertAlmostEqual(matrix[j][j], 1.0)
            for k in range(5):
                self.assertAlmostEqual(matrix[j][k], matrix[k][j])

    def test_radiative_flux_boosts_coupling_energy(self):
        node = VoidCouplingNode("v", {"coupling_constant": 2})
        a = node.compute({"edge_phases": [0] * 5, "radiative_flux": 0})["coupling_energy"]
        b = node.compute({"edge_phases": [0] * 5, "radiative_flux": 3})["coupling_energy"]
        self.assertEqual(a, 1.0)
        self.assertEqual(b, 4.0)

    def test_vector_potential_flux_calculation(self):
        node = VoidCouplingNode("v")
        result = node.compute({"edge_phases": [0] * 5,
                               "vector_potential_samples": [(2, 0.5), (3, 2), -1.0]})
        self.assertEqual(result["cavity_flux"], 6.0)
        self.assertEqual(node.compute({"edge_phases": [0] * 5,
                                       "vector_potential_samples": []})["cavity_flux"], 0.0)

    def test_edge_phases_length_validation(self):
        for values in ([], [1], [1, 2, 3, 4, 5, 6]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                VoidCouplingNode("v").compute({"edge_phases": values})

    def test_non_dict_inputs_rejected(self):
        with self.assertRaises(TypeError):
            VoidCouplingNode("v").compute([0, 0, 0, 0, 0])

    def test_pipeline_integration_with_graph(self):
        graph = Graph()
        graph.add_node(StrainTensorNode("strain", {"critical_threshold": 0.5}))
        graph.add_node(PermittivityEnvelopeNode("permittivity"))
        graph.add_node(VoidCouplingNode("void"))
        for port in ("trace", "frobenius_dev", "is_critical"):
            graph.connect("strain", port, "permittivity", port)
        graph.connect("permittivity", "radiative_flux", "void", "radiative_flux")
        results = graph.run({"strain": {"tensor": [[1.0, 0.0], [0.0, -1.0]]},
                             "void": {"edge_phases": [0.2] * 5}})
        self.assertAlmostEqual(results["permittivity"]["radiative_flux"], 0.85)
        self.assertAlmostEqual(results["void"]["phase_coherence"], 1.0)
        self.assertAlmostEqual(results["void"]["coupling_energy"], 0.5 * 1.85)

    def test_bridge_offset_and_flux_validation(self):
        n = VoidCouplingNode("v", {"bridge_phase_offset": 1.0})
        self.assertAlmostEqual(n.compute({"edge_phases": [0] * 5})["bridge_phase"], 1.0)
        for flux in (-1, True, float("nan")):
            with self.subTest(flux=flux), self.assertRaises(ValueError):
                n.compute({"edge_phases": [0] * 5, "radiative_flux": flux})

    def test_float_samples_and_nonfinite_phase_rejected(self):
        res = VoidCouplingNode("v").compute({"edge_phases": [0] * 5,
                                               "vector_potential_samples": [1.5, 2.5]})
        self.assertEqual(res["cavity_flux"], 4.0)
        with self.assertRaises(ValueError):
            VoidCouplingNode("v").compute({"edge_phases": [0, 0, 0, 0, float("inf")]})


if __name__ == "__main__":
    unittest.main()
