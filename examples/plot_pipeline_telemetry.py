"""
Plot Telemetry and Topological Metrics for SDF Lattice Pipeline v0.4.
Reads JSON output from examples/output/pipeline_v04_full_execution.json
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def main():
    json_path = Path("examples/output/pipeline_v04_full_execution.json")
    if not json_path.exists():
        print(f"[-] Error: Telemetry file {json_path} not found. Run pipeline first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Extract telemetry indices
    strain = data.get("strain", {})
    void_coup = data.get("void_coupling", {})
    permittivity = data.get("permittivity", {})
    closure = data.get("closure", {})

    coupling_matrix = np.array(void_coup.get("coupling_matrix", np.eye(5)))

    # 2. Figure layout
    fig, axs = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        "SDF-Lattice v0.4 Pipeline Telemetry & Topological Metrics",
        fontsize=15,
        fontweight="bold",
    )

    # 1. Heatmap of the 5-edge cavity coupling matrix
    im1 = axs[0, 0].imshow(coupling_matrix, cmap="viridis", vmin=0.98, vmax=1.0)
    axs[0, 0].set_title(r"5-Edge Cavity Coupling Matrix ($C_{ij}$)", fontsize=11, fontweight="bold")
    axs[0, 0].set_xlabel("Edge Index j")
    axs[0, 0].set_ylabel("Edge Index i")
    fig.colorbar(im1, ax=axs[0, 0], fraction=0.046, pad=0.04)

    # 2. Stabilizers of the stress tensor and permittivity
    invariants = [
        "Hydrostatic",
        "Frobenius Dev",
        "Permittivity",
        "Radiative Flux",
    ]
    vals = [
        strain.get("hydrostatic", 0.0),
        strain.get("frobenius_dev", 0.0),
        permittivity.get("effective_permittivity", 0.0),
        permittivity.get("radiative_flux", 0.0),
    ]
    bars = axs[0, 1].bar(
        invariants, vals, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    )
    axs[0, 1].set_title("Strain Deviatoric & Dielectric Invariants", fontsize=11, fontweight="bold")
    axs[0, 1].grid(True, linestyle="--", alpha=0.5)
    for bar in bars:
        yval = bar.get_height()
        axs[0, 1].text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.03,
            f"{yval:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # 3. Phase locking and bridging phase
    metrics_names = ["Phase Coherence", "Bridge Phase / 2pi", "Coupling Energy"]
    bridge_phase_norm = void_coup.get("bridge_phase", 0.0) / (2 * np.pi)
    metrics_vals = [
        void_coup.get("phase_coherence", 0.0),
        bridge_phase_norm,
        void_coup.get("coupling_energy", 0.0),
    ]
    bars_phase = axs[1, 0].bar(
        metrics_names, metrics_vals, color=["#9467bd", "#8c564b", "#e377c2"]
    )
    axs[1, 0].set_title("Topological Phase-Locking Metrics", fontsize=11, fontweight="bold")
    axs[1, 0].set_ylim(0, 1.25)
    axs[1, 0].grid(True, linestyle="--", alpha=0.5)
    for bar in bars_phase:
        yval = bar.get_height()
        axs[1, 0].text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.02,
            f"{yval:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # 4. Friedman-dependence balancing
    closure_metrics = ["Causality Residual", "Energy Deficit"]
    closure_vals = [
        closure.get("causality_residual", 0.0),
        closure.get("energy_deficit", 0.0),
    ]
    status = closure.get("closure_status", "UNKNOWN")
    axs[1, 1].bar(
        closure_metrics, closure_vals, color=["#bcbd22", "#17becf"], width=0.45
    )
    axs[1, 1].set_title(
        f"Pre-Friedmann Closure Balance (Status: {status})", fontsize=11, fontweight="bold"
    )
    axs[1, 1].grid(True, linestyle="--", alpha=0.5)
    axs[1, 1].set_ylim(0, max(closure_vals) * 1.35)
    for i, v in enumerate(closure_vals):
        axs[1, 1].text(i, v + 0.015, f"{v:.4f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    out_file = Path("examples/output/pipeline_v04_telemetry_plot.png")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[✓] High-resolution telemetry plot saved successfully to: {out_file}")


if __name__ == "__main__":
    main()
