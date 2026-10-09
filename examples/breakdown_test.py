import json
import random

# Structural breakdown test with 200% noise (Inhomogeneity 200%)
# Push the noise amplitude far enough to locate where the system leaves the stable regime
num_voids = 20
graph_data = {
    "version": "v0.4_breakdown_test",
    "nodes": [],
    "connections": []
}

for i in range(num_voids):
    # Noise in [-2.0, 2.0]
    noise = random.uniform(-2.0, 2.0) 
    coupling = 1.0 + noise
    # Guard against negative coupling (unless the physics demands it)
    coupling = max(0.1, coupling) 
    graph_data["nodes"].append({
        "id": f"void_{i}",
        "type": "SupercellCouplingNode",
        "params": {"coupling_strength": coupling}
    })

for i in range(num_voids - 1):
    graph_data["connections"].append({
        "source": f"void_{i}",
        "target": f"void_{i+1}",
        "type": "supercell_link"
    })

with open("config/breakdown_graph.json", "w") as f:
    json.dump(graph_data, f, indent=4)

print("200%-noise breakdown test saved to config/breakdown_graph.json.")
