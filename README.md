# SDF Lattice Master v0.3.5

[![DOI](https://zenodo.org/badge/1412325942.svg)](https://doi.org/10.5281/zenodo.23382706)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A framework for Structured Deformation Fields (SDF)...


## Overview

`sdf_lattice` models dynamic deformation, elastodynamic strain, and non-trivial Berry curvature in engineered optical/mechanical micro-cavities. It is designed for quantum electrodynamics (QED) and polaritonic simulation lattices.

### Core Features

- **Strain & Permittivity Coupling:** Models anisotropic stress tensors and induced permittivity envelopes.
- **Topological & Berry Dynamics:** Tracks phase winding and adiabatic connections across dynamic cavities.
- **Peristaltic Pumping & Causality:** Time-dependent boundary perturbations with retarded Green function kernels.
- **Berry Torque Coupling (optional):** Phenomenological torque and gap-stress pathway from Berry curvature and phase drive; units, sign convention, and limitations documented in `docs/berry_torque_gap_stress.md`.
- **Execution Engine:** Directed Acyclic Graph (DAG) pipeline with topological sorting, boundary validation, and telemetry.

## Directory Structure

```text
SDF_Lattice_Master_v0.3.4/
├── config/             # Graph definitions and schema specifications
├── docs/               # Technical documentation and authoring guides
├── examples/           # Simulation experiments and plotting scripts
├── sdf_lattice/        # Core execution engine and node definitions
├── tests/              # Test suite
├── pyproject.toml       # Packaging metadata and dependencies
└── requirements-dev.txt# Development and testing requirements
```

## Installation

Requirements: Python >= 3.10 and NumPy >= 1.24.0.

```bash
cd SDF_Lattice_Master_v0.3.4
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

## Tests

Run the verification suite from the project directory:

```bash
pytest
```

## Authoring Custom Nodes

Custom nodes can subclass `Node` from `sdf_lattice.nodes.base`:

```python
from sdf_lattice.nodes.base import Node

class CustomPhaseNode(Node):
    def compute(self, inputs: dict) -> dict:
        return {"output_field": inputs.get("input_field", 0.0) * 1.5}
```

Register the node in `sdf_lattice/registry.py` if it should be available to declarative graph configurations. See `docs/node-authoring.md`.

## Citation

See `CITATION.cff`. Contact: adelgachkar@gmail.com.

**Zenodo (first record):** Concept DOI [10.5281/zenodo.23271142](https://doi.org/10.5281/zenodo.23271142) · v0.3.4 version DOI [10.5281/zenodo.23271143](https://doi.org/10.5281/zenodo.23271143)

## License

Licensed under the MIT License; see `LICENSE`.
