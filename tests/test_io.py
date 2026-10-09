import unittest
from sdf_lattice import Graph
from sdf_lattice.nodes.base import PassthroughNode
from sdf_lattice.io import graph_to_dict

class IoTests(unittest.TestCase):
    def test_graph_shape(self):
        g = Graph(); g.add_node(PassthroughNode("only"))
        data = graph_to_dict(g)
        self.assertEqual(data["nodes"][0]["id"], "only")
        self.assertEqual(data["edges"], [])
