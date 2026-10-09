# Release Log: SDF-Lattice Master v0.3.4

## Version 0.3.3 Changes
- **Metadata Synchronization:** Aligned project specifications and release configurations across all core components.
- **Peristaltic Pump Integration:** Added phase budgeting dynamics to `PeristalticPumpNode`.
- **Test Suite Expansion:** Broadened automated verification test coverage across quantum cavity coupling pipelines.
- **Documentation English Standardization:** Replaced legacy multilingual notes with comprehensive scientific documentation.
- **Theoretical Scope Disclaimer:** Computational model outputs are simulation benchmarks and should not be construed as direct empirical validation without laboratory verification.

## Milestone Status
- **Phase 1 (Geometric Frustration & Deficit Angles):** Completed & verified via `verify_phase1_alpha.py`.
- **Phase 2 (Berry Dynamics & Retarded Causality):** Fully passed with stable Lyapunov lock ($\lambda = -0.0784$).
- **Phase 3 (Supercell Coupling Dynamics):** Stable under non-linear resonance driving regimes.


## Version 0.3.4 Changes
- Added optional `BerryTorqueNode` phenomenological coupling from Berry curvature and phase drive to torque and equivalent gap traction/stress.
- Added backward-compatible optional stress addition in `StrainTensorNode`; strain remains distinct from stress.
- Added focused tests and `docs/berry_torque_gap_stress.md` documenting units, sign convention, scope, and limitations.
- The coupling is a model-level ansatz only; it is not a first-principles result or experimentally validated.
- Contact: adelgachkar@gmail.com
