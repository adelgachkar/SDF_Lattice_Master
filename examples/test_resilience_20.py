import json
import random

# Stress test with 50% noise (Inhomogeneity 50%)
num_voids = 20
graph_data = {
    "version": "v0.4_stress_test_limit",
    "nodes": [],
    "connections": []
}

# Apply broad noise to the coupling
for i in range(num_voids):
    noise = random.uniform(-0.5, 0.5) 
    coupling = 1.0 + noise
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

with open("config/graph_stress_limit_20.json", "w") as f:
    json.dump(graph_data, f, indent=4)

print("50%-noise stress test saved to config/graph_stress_limit_20.json.")
