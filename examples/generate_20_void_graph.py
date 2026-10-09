import json

# 20-void network settings (scaling stress test)
num_voids = 20
graph_data = {
    "version": "v0.4_scaled_20",
    "nodes": [],
    "connections": []
}

# Generate nodes with a symmetric coupling distribution
for i in range(num_voids):
    # Preserve symmetry to prevent premature instability
    coupling = 1.0 + (i * 0.02) 
    graph_data["nodes"].append({
        "id": f"void_{i}",
        "type": "SupercellCouplingNode",
        "params": {"coupling_strength": coupling}
    })

# Build chained connections
for i in range(num_voids - 1):
    graph_data["connections"].append({
        "source": f"void_{i}",
        "target": f"void_{i+1}",
        "type": "supercell_link"
    })

with open("config/graph_20_voids.json", "w") as f:
    json.dump(graph_data, f, indent=4)

print("20-void configuration saved to config/graph_20_voids.json.")
