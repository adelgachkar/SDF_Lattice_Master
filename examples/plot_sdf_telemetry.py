"""
plot_sdf_telemetry.py
Visualizes the multi-scenario telemetry data from SDF-Lattice v0.3.
"""

import os
import csv
import matplotlib.pyplot as plt

def load_telemetry(csv_path):
    scenarios = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sc_name = row["scenario"]
            if sc_name not in scenarios:
                scenarios[sc_name] = {
                    "step": [],
                    "phase_coherence": [],
                    "permittivity": [],
                    "causality_residual": [],
                    "energy_deficit": [],
                    "coupling_energy": []
                }
            scenarios[sc_name]["step"].append(int(row["step"]))
            scenarios[sc_name]["phase_coherence"].append(float(row.get("phase_coherence", 0.0)))
            scenarios[sc_name]["permittivity"].append(float(row.get("effective_permittivity", 1.0)))
            scenarios[sc_name]["causality_residual"].append(float(row.get("causality_residual", 0.0)))
            scenarios[sc_name]["energy_deficit"].append(float(row.get("energy_deficit", 0.0)))
            scenarios[sc_name]["coupling_energy"].append(float(row.get("coupling_energy", 0.0)))
    return scenarios

def plot_scenarios(scenarios, output_image_path):
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    colors = {
        "1_BOUND_STABLE": "#1f77b4",
        "2_PHASE_LEAKAGE": "#ff7f0e",
        "3_BIFURCATION": "#d62728"
    }
    
    # 1. Phase Coherence
    ax1 = axes[0]
    for sc_name, data in scenarios.items():
        color = colors.get(sc_name, "black")
        ax1.plot(data["step"], data["phase_coherence"], marker='o', label=sc_name, color=color, linewidth=2)
    ax1.set_ylabel("Phase Coherence (|R|)", fontsize=11)
    ax1.set_title("SDF-Lattice v0.3 Dynamic Response Analysis", fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="best")
    ax1.set_ylim(-0.05, 1.1)

    # 2. Effective Permittivity
    ax2 = axes[1]
    for sc_name, data in scenarios.items():
        color = colors.get(sc_name, "black")
        ax2.plot(data["step"], data["permittivity"], marker='s', label=sc_name, color=color, linewidth=2)
    ax2.set_ylabel("Effective Permittivity (ε_eff)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="best")

    # 3. Causality Residual
    ax3 = axes[2]
    for sc_name, data in scenarios.items():
        color = colors.get(sc_name, "black")
        ax3.plot(data["step"], data["causality_residual"], marker='^', label=f"{sc_name} (Residual)", color=color, linewidth=2)
    ax3.set_xlabel("Simulation Step", fontsize=11)
    ax3.set_ylabel("Causality Residual", fontsize=11)
    ax3.grid(True, linestyle="--", alpha=0.6)
    ax3.legend(loc="best")

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    print(f"[*] Plot successfully saved to: {output_image_path}")

if __name__ == "__main__":
    csv_file = os.path.join("examples", "output", "telemetry_results.csv")
    output_png = os.path.join("examples", "output", "sdf_telemetry_plot.png")
    
    if os.path.exists(csv_file):
        data = load_telemetry(csv_file)
        plot_scenarios(data, output_png)
    else:
        print(f"Error: {csv_file} not found. Please run run_sdf_multi_scenario.py first.")
