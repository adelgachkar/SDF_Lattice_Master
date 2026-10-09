import unittest
import numpy as np
from sdf_lattice.nodes.supercell_coupling import SupercellCouplingNode


class TestSupercellCouplingNode(unittest.TestCase):
    def setUp(self):
        self.node = SupercellCouplingNode("supercell_test")

    def test_synchronized_supercell(self):
        # 3 voids with identical synchronized phases
        phases = np.array([
            [0.1, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1, 0.1],
        ])
        out = self.node.compute({"void_phase_matrix": phases})
        self.assertAlmostEqual(out["collective_coherence"], 1.0, places=4)
        self.assertTrue(out["supercell_locked"])

    def test_desynchronized_supercell(self):
        # 2 voids with orthogonal phase bifurcations
        phases = np.array([
            [0.0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5],
            [0.0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5],
        ])
        out = self.node.compute({"void_phase_matrix": phases})
        self.assertAlmostEqual(out["collective_coherence"], 0.0, places=4)
        self.assertFalse(out["supercell_locked"])


if __name__ == "__main__":
    unittest.main()
