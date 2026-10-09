import unittest
from sdf_lattice import Graph
from sdf_lattice.nodes.base import PassthroughNode

class CoreTests(unittest.TestCase):
    def test_execution(self):
        g = Graph()
        g.add_node(PassthroughNode("a"))
        g.add_node(PassthroughNode("b"))
        g.connect("a", "x", "b", "y")
        self.assertEqual(g.run({"a": {"x": 7}})["b"]["y"], 7)

    def test_cycle_rejected(self):
        g = Graph()
        g.add_node(PassthroughNode("a"))
        g.add_node(PassthroughNode("b"))
        g.connect("a", "x", "b", "x")
        g.connect("b", "x", "a", "x")
        with self.assertRaises(ValueError):
            g.run()

if __name__ == "__main__":
    unittest.main()
