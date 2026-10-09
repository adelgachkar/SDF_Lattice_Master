import math
import unittest

from sdf_lattice import Graph
from sdf_lattice.nodes import PermittivityEnvelopeNode, StrainTensorNode


class PermittivityEnvelopeTests(unittest.TestCase):
    def test_defaults_and_formulas(self):
        node = PermittivityEnvelopeNode("p")
        result = node.compute({"trace": 2.0, "frobenius_dev": 3.0, "is_critical": True})
        eps = 1.0 * (1.0 + 0.15 * 2.0)
        energy = 0.5 * eps * (2.0**2 + 3.0**2)
        self.assertAlmostEqual(result["effective_permittivity"], eps)
        self.assertAlmostEqual(result["reactive_energy_density"], energy)
        self.assertAlmostEqual(result["radiative_flux"], 0.85 * energy)
        self.assertEqual(result["confinement_status"], "radiative")

    def test_configured_parameters_and_noncritical_state(self):
        node = PermittivityEnvelopeNode("p", {"epsilon_0": 2, "photoelastic_coupling": -0.25,
                                                "radiative_leak_rate": 0.4})
        result = node.compute({"eps_hydro": 2, "shear_norm": 1, "is_critical": False})
        self.assertAlmostEqual(result["effective_permittivity"], 1.0)
        self.assertAlmostEqual(result["reactive_energy_density"], 2.5)
        self.assertEqual(result["radiative_flux"], 0.0)
        self.assertEqual(result["confinement_status"], "confined")

    def test_truthy_critical_and_boundary_rates(self):
        for rate, expected in ((0.0, 0.0), (1.0, 0.575)):
            result = PermittivityEnvelopeNode("p", {"radiative_leak_rate": rate}).compute(
                {"trace": 1, "frobenius_dev": 0, "is_critical": 1})
            self.assertAlmostEqual(result["radiative_flux"], expected)
            self.assertEqual(result["confinement_status"], "radiative")

    def test_numeric_validation_for_parameters(self):
        invalid = [True, "1", None, float("nan"), float("inf"), -float("inf")]
        for name in ("epsilon_0", "photoelastic_coupling", "radiative_leak_rate"):
            for value in invalid:
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    PermittivityEnvelopeNode("p", {name: value})
        for value in (0, -1):
            with self.subTest(epsilon_0=value), self.assertRaises(ValueError):
                PermittivityEnvelopeNode("p", {"epsilon_0": value})
        for value in (-0.01, 1.01):
            with self.subTest(rate=value), self.assertRaises(ValueError):
                PermittivityEnvelopeNode("p", {"radiative_leak_rate": value})

    def test_numeric_validation_for_inputs(self):
        node = PermittivityEnvelopeNode("p")
        for port in ("trace", "frobenius_dev"):
            for value in (True, "1", None, float("nan"), float("inf")):
                data = {"trace": 1, "frobenius_dev": 1, "is_critical": False}
                data[port] = value
                with self.subTest(port=port, value=value), self.assertRaises(ValueError):
                    node.compute(data)

    def test_required_inputs_and_aliases(self):
        node = PermittivityEnvelopeNode("p")
        with self.assertRaises(KeyError):
            node.compute({})
        with self.assertRaises(KeyError):
            node.compute({"trace": 0})
        with self.assertRaises(KeyError):
            node.compute({"trace": 0, "frobenius_dev": 0})
        result = node.compute({"eps_hydro": 0, "shear_norm": 2, "is_critical": False})
        self.assertEqual(result["effective_permittivity"], 1.0)
        self.assertEqual(result["reactive_energy_density"], 2.0)

    def test_inputs_must_be_mapping_and_overflow_is_rejected(self):
        node = PermittivityEnvelopeNode("p")
        with self.assertRaises(TypeError):
            node.compute([])
        with self.assertRaises(ValueError):
            node.compute({"trace": 1e308, "frobenius_dev": 1e308, "is_critical": True})

    def test_chain_strain_into_permittivity(self):
        graph = Graph()
        graph.add_node(StrainTensorNode("strain", {"critical_threshold": 0.5}))
        graph.add_node(PermittivityEnvelopeNode("permittivity"))
        graph.connect("strain", "trace", "permittivity", "trace")
        graph.connect("strain", "frobenius_dev", "permittivity", "frobenius_dev")
        graph.connect("strain", "is_critical", "permittivity", "is_critical")
        results = graph.run({"strain": {"tensor": [[1.0, 0.0], [0.0, -1.0]]}})
        self.assertTrue(results["strain"]["is_critical"])
        self.assertAlmostEqual(results["permittivity"]["effective_permittivity"], 1.0)
        self.assertAlmostEqual(results["permittivity"]["reactive_energy_density"], 1.0)
        self.assertAlmostEqual(results["permittivity"]["radiative_flux"], 0.85)

    def test_public_export(self):
        from sdf_lattice.nodes import __all__
        self.assertIn("PermittivityEnvelopeNode", __all__)
        self.assertEqual(PermittivityEnvelopeNode.type_name, "permittivity_envelope")


if __name__ == "__main__":
    unittest.main()
