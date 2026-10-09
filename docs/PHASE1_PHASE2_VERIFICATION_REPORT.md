# Computational Verification Report — SDF-Lattice Phases 1 & 2

**Record ID:** `SDF-VAL-V03-001` · **Target code version:** 0.3.4
**Scope:** software testing, modeled geometry, numerical screening, and simulated dynamic behavior.

> This report registers model/code results; agreement of a computed number with a measured constant is, by itself, neither independent physical proof nor empirical validation of the model. Results depend on model conventions and parameter choices.

## 1. Phase 1 — Geometry and fine-structure screening

### 1.1 Geometric deficit angle
For five regular tetrahedra sharing a common edge, the dihedral angle of each is

$$\theta_d=\arccos(1/3)\approx70.528779^\circ$$
$$5\theta_d\approx352.643897^\circ,\qquad \Delta_{\mathrm{deficit}}=360^\circ-5\theta_d\approx7.356103^\circ.$$

This quantity is the geometric deficit angle in the defined arrangement.

### 1.2 Raw geometric value versus screened value
In the reported parameterization, the model baseline/raw value is $\Phi_{\mathrm{geom}}=146.82$. The Berry screening factor, proportional to two of thirty structural channels, is defined as

$$\eta_{\mathrm{screen}}=\frac{2}{30}=\frac{1}{15}\approx0.0666667,\qquad f_{\mathrm{screen}}=1-\eta_{\mathrm{screen}}=\frac{28}{30}.$$

Hence the screened value — not the raw geometric value — is

$$\Phi_{\mathrm{screened}}=\Phi_{\mathrm{geom}}f_{\mathrm{screen}}=146.82\left(1-\frac{2}{30}\right)=146.82\times\frac{28}{30}=137.032.$$

The numbers 146.82 and 137.032 are therefore not in contradiction: the former is the model's raw/geometric value, the latter its value after the screening correction. In this report, 137.032 appears as the screened output and 146.82 as the geometric input.

| Quantity | Model value | CODATA comparison | Absolute difference | Approx. relative difference |
|---|---:|---:|---:|---:|
| Screened value $\Phi_{\mathrm{screened}}$ | 137.032000 | 137.035999 | 0.003999 | 0.0029% |

This table is a numerical comparison, not a claim of deriving a fundamental constant from accepted principles or of independent empirical confirmation.

## 2. Phase 2 — Berry dynamics and model stability

The reported parameters come from the example-script runs: Berry phase transfer $\Delta\gamma=1.9025\,\mathrm{rad}$, modeled output power $P_{\mathrm{jet}}=0.931314$, surrogate Lyapunov exponent $\lambda_{\mathrm{proxy}}=-0.0784$, and frequency variance $\sigma_f^2=8.73622\times10^{-5}\,\mathrm{Hz}^2$. These describe the model execution and must not be taken as measurements without a complete specification of the numerical method, initial conditions, units, and independent reproduction. The negative proxy within the simulated range is consistent with stable behavior; it is not a mathematical stability guarantee for all modes.

## 3. Causality constraint and smoothing

`RetardedCausalityNode` computes a minimum propagation time as $t_{\min}=d/v_{\max}$, blocks spacelike signals in strict mode, and applies an exponential smoothing filter to allowed transitions. A non-negative damping parameter applies distance-dependent amplitude decay. The shared phase budget in version 0.3.3+ includes $\tau_{\mathrm{continuum}}=0.032$ and $\Delta t_{\mathrm{sampling}}=0.004$ with ratio 8.

This implementation is a computational model; physical claims about microcausality or propagation in a fundamental theory require separate assumptions and proofs.

## 4. Validation status

Unit tests, interface compatibility, and specified numerical are checked. For the current-run result and exact test counts, defer to the unittest output of the shipped package version.
