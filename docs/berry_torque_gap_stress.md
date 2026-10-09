# Berry torque contribution to effective gap stress

## Scope

`BerryTorqueNode` in `sdf_lattice/nodes/berry_torque.py` implements an optional phenomenological model coupling. It is not a first-principles derivation, does not follow from the existing Berry phase dynamics implementation, and has not been experimentally validated. The coefficient is a user-specified calibration/model parameter.

## Relation, symbols, units, and sign

The model uses

`T = kappa * q * Omega`,

`T_n = T dot n_hat`, and `sigma_B = T_n / (A * ell)`.

`Omega` is the supplied Berry-curvature pseudovector in m^-2; `q` is the phase rate in s^-1; `kappa` is the phenomenological coefficient in N m^3 s; `T` is torque in N m; `n_hat` is the normalized gap-normal vector; `A` is the positive gap/reference area in m^2; `ell` is the positive gap lever arm in m; and `sigma_B` is a signed effective traction/stress in Pa. If supplying a dimensionless phase imbalance `dphi`, specify a positive `phase_rate_scale` in s^-1 and the node uses `q = dphi * phase_rate_scale`. The default rate scale is 1 s^-1. Area and length inputs use SI units.

The sign of `sigma_B` follows the supplied orientation of `Omega` and `n_hat`: reversing the phase drive or normal reverses the projected sign. No absolute value is applied. Zero normals, area, or lever arm are rejected; non-finite and boolean numeric inputs are rejected.

## Use and strain-pathway integration

Create `BerryTorqueNode("berry_torque")` and call it with `berry_curvature`, exactly one of `phase_rate` or `phase_imbalance`, `gap_normal`, `lever_arm`, `coupling_coefficient`, and `gap_area` (or `reference_area`). Its `gap_stress` output can be connected to the strain node as `berry_gap_stress`; alternatively pass the complete output mapping as `berry_torque_result`. The strain node optionally accepts `base_gap_stress` and reports `effective_gap_stress = base_gap_stress + berry_gap_stress`. Strain outputs remain unchanged and dimensionless; no stress is inferred from strain. With no optional Berry stress input, its existing output mapping is unchanged.

## Limitations

The coefficient and inputs are not prescribed by this package and require a separately justified modeling choice. The mapping is a dimensional phenomenological ansatz only. Numerical/unit tests verify implementation behavior, not physical validity or empirical agreement.
