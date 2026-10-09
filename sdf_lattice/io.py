"""JSON serialization helpers (stdlib only)."""
import json
from pathlib import Path
from .core import Graph

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def save_json(data, path):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def graph_to_dict(graph):
    return {"nodes": [n.describe() for n in graph.nodes.values()], "edges": [e.__dict__ for e in graph.edges]}
