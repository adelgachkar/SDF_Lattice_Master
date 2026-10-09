# SDF-Lattice Master v0.3.4: Project Architecture & Map of Content (MOC)

Comprehensive architectural index and relational map for the SDF-Lattice quantum cavity simulation framework.

---

## 1. Theoretical Documentation & Technical Reports
- [[docs/5_tetrahedron_cavity_whitepaper.en.md]] — Foundational whitepaper on 5-tetrahedron quantum cavity dynamics.
- [[docs/5_tetrahedron_model_formulas.json]] — Symbolic and numerical parameters of cavity geometry.
- [[docs/tetra_report.md]] — Technical report on Lenz retardation correction and chiral polar jets.
- [[docs/PHASE1_PHASE2_VERIFICATION_REPORT.md]] — Consolidated verification report for Phase 1 & Phase 2 dynamics.
- [[docs/berry_phase2_verification_report.md]] — Verification summary of Berry phase locking and Blandford-Znajek jet emissions.
- [[docs/berry_torque_gap_stress.md]] — Phenomenological Berry torque and optional gap-stress coupling; scope, units, and sign convention.
- [[docs/node-authoring.md]] — Architectural guide for authoring custom graph execution nodes.

---

## 2. Computational Core & Quantum Pipeline Nodes (`sdf_lattice/`)
- [[sdf_lattice/core.py]] — Directed acyclic graph (DAG) engine and state manager.
- [[sdf_lattice/registry.py]] — Node factory and dynamic registry.
- [[sdf_lattice/io.py]] — Serialization, telemetry exports, and graph I/O.
- [[sdf_lattice/nodes/base.py]] — Abstract base class for pipeline execution nodes.
- [[sdf_lattice/nodes/berry_dynamics.py]] — Non-linear Berry geometric phase and Lyapunov stability node.
- [[sdf_lattice/nodes/berry_torque.py]] — Optional phenomenological Berry-curvature torque and effective gap-stress node.
- [[sdf_lattice/nodes/peristaltic_pump.py]] — Phase budgeting and dynamic peristaltic pumping node.
- [[sdf_lattice/nodes/retarded_causality.py]] — Retarded causality and Lenz back-reaction node.
- [[sdf_lattice/nodes/closure_constraints.py]] — Topological phase-closure constraint solver.
- [[sdf_lattice/nodes/void_coupling.py]] — Inter-void coupling matrix computation.
- [[sdf_lattice/nodes/supercell_coupling.py]] — Supercell lattice feedback dynamics.
- [[sdf_lattice/nodes/permittivity.py]] — Effective dielectric response and screening node.
- [[sdf_lattice/nodes/strain.py]] — Non-linear lattice strain tensor calculation.

---

## 3. Simulation & Verification Pipelines (`examples/`)
- [[examples/verify_phase1_alpha.py]] — Phase 1 verification script (alpha deficit angle convergence).
- [[examples/verify_phase2_berry.py]] — Phase 2 Berry phase locking and supercritical jet validation.
- [[examples/5_tetrahedron_quantum_cavity_engine.py]] — End-to-end 5-tetrahedron cavity engine execution.
- [[examples/run_sdf_closure_sim.py]] — Full closure simulation pipeline.
- [[examples/run_supercell_sim.py]] — Supercell feedback dynamic execution.
- [[examples/test_resilience_20.py]] — High-stress topological breakdown and resilience tests.

---

## 4. Telemetry & Visualization
- [[examples/plot_pipeline_telemetry.py]] — Pipeline state telemetry plotter.
- [[examples/plot_sdf_telemetry.py]] — Cavity parameter timeseries plotter.
- [[examples/plot_supercell_telemetry.py]] — Supercell coupling phase portrait generator.
- [[examples/output/pipeline_v04_execution.json]] — Verified execution benchmark results.

---

## 5. Configuration & Verification Suites
- [[config/graph_20_voids.json]] — Standard 20-void reference topology.
- [[config/graph_stress_limit_20.json]] — Supercritical stress testing configuration.
- [[tests/]] — Complete unit test suite (100% pass mark via pytest).
