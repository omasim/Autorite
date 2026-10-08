# RP002A — Preregistration v0.1
**Question:** In finite partially observed stochastic processes, when does recursively updated history recover predictive distinctions unavailable in current observation?

**Scope:** finite/discrete/stochastic/partially observed/passive; stationary within episodes; known predictive query; no agent actions/self-modification.

**Worlds:** E0 present sufficient; E1 observation aliases predictive states/history disambiguates; E2 history varies but is future-irrelevant.

**Baselines:** B0 current observation; B1 finite raw history; B2 fixed-size recursive learned state; B3 generator-defined oracle.

**Primary hypothesis:** history-sensitive representations outperform B0 in E1, but not systematically in E0/E2.

**Controls:** generator sanity checks before model comparison. Primary metric candidate: log loss with effect size/uncertainty and calibration diagnostics.

**Interpretation lock:** does not establish universal/fundamental memory or full-history retention.

**Decision matrix:** E0 advantage → leakage/capacity investigation; E1 no advantage → generator/model/optimization diagnosis; B1≈B2 → no demonstrated recurrent-state special advantage; unexpected → SURPRISE/diagnostic before revision.
