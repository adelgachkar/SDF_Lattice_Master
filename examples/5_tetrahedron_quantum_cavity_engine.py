#!/usr/bin/env python3
"""
Phenomenological simulator for a five-tetrahedron quantum-cavity concept.
This is a computational toy model, not a validated physical theory.
Outputs: CSV time series, JSON metadata/formulas, and a 300-dpi multi-panel PNG.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Setup output path relative to script location to ensure portability
OUT = Path(__file__).resolve().parent / 'output'
OUT.mkdir(parents=True, exist_ok=True)

SEED = 7
rng = np.random.default_rng(SEED)

# Reference quantities
N = 5
angular_deficit_deg = 7.36
angular_deficit = np.deg2rad(angular_deficit_deg)
V0 = 146.82
edge_loss = 2/30
coupling_retention = 1 - edge_loss
alpha_inv = 137.036

# Time grid and state variables
T, dt = 80.0, 0.02
t = np.arange(0, T + dt/2, dt)
M = len(t)
phase = np.zeros((M, N))
omega = np.zeros((M, N))
temp = np.zeros(M)
choke = np.zeros(M)
jet_n = np.zeros(M)
jet_s = np.zeros(M)
jet_total = np.zeros(M)
energy = np.zeros(M)
berry = np.zeros(M)

phase[0] = np.linspace(0, 2*np.pi*(N-1)/N, N) + rng.normal(0, .03, N)
temp[0] = 0.15

# System dynamics parameters
gamma = np.array([1, -1, 1, -1, 1.], float)
phi_drive = np.array([0.00, .21, -.17, .12, -.09])
base_omega = 1.0 + 0.12*np.cos(2*np.pi*np.arange(N)/N)
K = 0.82 * coupling_retention
thermal_coeff = 0.018
cooling = 0.07
heat_gain = 0.035

def wrap(x):
    return (x + np.pi) % (2*np.pi) - np.pi

# Main simulation loop
for k in range(M-1):
    order = np.abs(np.mean(np.exp(1j*phase[k])))
    omega[k] = base_omega + gamma * angular_deficit/np.pi*0.10 + thermal_coeff*temp[k]
    coupling = K/N * np.sum(np.sin(phase[k][None, :] - phase[k][:, None]), axis=1)
    berry_term = gamma * (angular_deficit/(2*np.pi)) * np.cos(phase[k] - phi_drive)
    dphi = omega[k] + coupling + berry_term
    phase[k+1] = phase[k] + dt*dphi
    dissipation = (1 - order) + edge_loss*0.25
    temp[k+1] = max(0, temp[k] + dt*(heat_gain*dissipation - cooling*temp[k]))
    lat = np.linspace(-np.pi/2, np.pi/2, N)
    equatorial_transmission = 1/(1+np.exp(-(np.abs(lat)-0.30)/0.06))
    choke[k] = 1 - np.mean(equatorial_transmission)
    polar_n = np.exp(-((lat-np.pi/2)/0.32)**2)
    polar_s = np.exp(-((lat+np.pi/2)/0.32)**2)
    coherence = order
    jet_n[k] = V0 * coupling_retention * coherence * np.mean(polar_n) * np.exp(-0.20*temp[k])
    jet_s[k] = V0 * coupling_retention * coherence * np.mean(polar_s) * np.exp(-0.20*temp[k])
    jet_total[k] = jet_n[k] + jet_s[k]
    energy[k] = V0 * (0.55 + 0.45*order) * np.exp(-edge_loss) * (1 + 0.02*temp[k])
    berry[k] = np.sum(gamma*wrap(phase[k] - phase[0]))/(2*np.pi)

# Finalize data
omega[-1] = base_omega + gamma * angular_deficit/np.pi*0.10 + thermal_coeff*temp[-1]
choke[-1] = choke[-2]
jet_n[-1] = jet_n[-2]
jet_s[-1] = jet_s[-2]
jet_total[-1] = jet_total[-2]
energy[-1] = energy[-2]
berry[-1] = berry[-2]
order_param = np.abs(np.mean(np.exp(1j*phase), axis=1))
phase_unwrapped = np.unwrap(phase, axis=0)

# Save results
csv_path = OUT / '5_tetrahedron_simulation_timeseries.csv'
png_path = OUT / '5_tetrahedron_quantum_cavity_engine_overview.png'

df = pd.DataFrame({
    'time': t, 'temperature_shift': temp, 'coherence_order': order_param,
    'equatorial_choke': choke, 'polar_jet_north': jet_n, 'polar_jet_south': jet_s,
    'polar_jet_total': jet_total, 'stored_energy_proxy': energy, 'net_berry_winding': berry
})
for i in range(N):
    df[f'phase_{i+1}'] = phase_unwrapped[:, i]
    df[f'omega_{i+1}'] = omega[:, i]

df.to_csv(csv_path, index=False)

# Visualization
plt.style.use('dark_background')
fig = plt.figure(figsize=(18, 12), constrained_layout=True)
gs = fig.add_gridspec(3, 2)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[2, 0])
ax6 = fig.add_subplot(gs[2, 1], projection='3d')

colors = plt.cm.plasma(np.linspace(.15, .9, N))
for i, c in enumerate(colors):
    ax1.plot(t, phase_unwrapped[:, i], color=c, lw=1.2, label=f'Tetra {i+1}')
ax1.set(title='Phase dynamics', xlabel='Time', ylabel='Unwrapped phase (rad)')
ax1.legend(ncol=3, fontsize=8)

ax2.plot(t, order_param, color='#56d8ff', label='Coherence R')
ax2.plot(t, temp, color='#ffb347', label='Thermal shift T')
ax2.set(title='Coherence and thermal shift', xlabel='Time')
ax2.legend()

ax3.plot(t, choke, color='#ff4fa3')
ax3.fill_between(t, 0, choke, color='#ff4fa3', alpha=.25)
ax3.set(title='Equatorial choke diagnostic', xlabel='Time', ylabel='C_eq (0-1)')
ax3.set_ylim(0, 1)

ax4.plot(t, jet_n, label='North polar jet', color='#63e6be')
ax4.plot(t, jet_s, label='South polar jet', color='#74c0fc')
ax4.plot(t, jet_total, '--', label='Total', color='white')
ax4.set(title='Polar jet emission proxy', xlabel='Time', ylabel='Amplitude')
ax4.legend()

ax5.plot(t, energy, color='#ffd43b', label='Stored-energy proxy')
ax5.plot(t, berry, color='#da77f2', label='Berry winding')
ax5.set(title='Energy proxy and Berry circulation', xlabel='Time')
ax5.legend()

xyz = np.c_[np.cos(2*np.pi*np.arange(N)/N), np.sin(2*np.pi*np.arange(N)/N), np.sin(4*np.pi*np.arange(N)/N)]
ax6.scatter([0], [0], [0], s=180, c='white', label='Central core')
for i, c in enumerate(colors):
    ax6.plot([0, xyz[i, 0]], [0, xyz[i, 1]], [0, xyz[i, 2]], color=c, lw=3)
    ax6.scatter(*xyz[i], s=100, c=[c])
    ax6.text(*xyz[i], f' T{i+1}', color=c)
ax6.set(title='Five-tetrahedron phase-space schematic', xlabel='x', ylabel='y', zlabel='z')
ax6.legend(loc='upper left', fontsize=8)

fig.suptitle('5-TETRAHEDRON QUANTUM CAVITY ENGINE - computational model', fontsize=18, fontweight='bold')
fig.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close(fig)

# =====================================================================
# Console Summary Output
# =====================================================================
print("\n" + "="*65)
print("  5-TETRAHEDRON QUANTUM CAVITY ENGINE : EXECUTION COMPLETE")
print("="*65)
print(f"[*] Steps simulated      : {M} (Duration: {T}s, dt: {dt}s)")
print(f"[*] Coherence Order (R)  : {order_param[-1]:.4f}")
print(f"[*] Thermal Shift (T)    : {temp[-1]:.4f}")
print(f"[*] Equatorial Choke     : {choke[-1]:.4f}")
print(f"[*] Net Polar Jet Total  : {jet_total[-1]:.4f}")
print(f"[*] Stored Energy Proxy  : {energy[-1]:.4f}")
print(f"[*] Net Berry Winding    : {berry[-1]:.4f}")
print("-"*65)
print(f"[+] Output CSV saved to  : {csv_path.name}")
print(f"[+] Overview PNG saved to: {png_path.name}")
print(f"[+] Full output path     : {OUT}")
print("="*65 + "\n")

# --- Export Run Summary to JSON ---
summary_data = {
    "simulation_parameters": {
        "steps_simulated": int(M),
        "duration_s": float(T),
        "dt": float(dt)
    },
    "final_metrics": {
        "coherence_order_r": round(float(order_param[-1]), 6),
        "thermal_shift_t": round(float(temp[-1]), 6),
        "equatorial_choke": round(float(choke[-1]), 6),
        "net_polar_jet_total": round(float(jet_total[-1]), 6),
        "stored_energy_proxy": round(float(energy[-1]), 6),
        "net_berry_winding": round(float(berry[-1]), 6)
    },
    "output_artifacts": {
        "csv_file": str(csv_path.name),
        "plot_file": str(png_path.name),
        "full_output_dir": str(OUT)
    }
}

summary_json_path = OUT / '5_tetrahedron_run_summary.json'
with open(summary_json_path, 'w') as f:
    json.dump(summary_data, f, indent=4)

print(f"[+] Run summary saved to : {summary_json_path.name}")
print("="*65 + "\n")
