# Intelligent water-infrastructure digital twin (research prototype)

This is a **research extension**, not a field-deployed or calibrated watershed digital twin. It supports the MSc research direction **Digital Twin Architectures for Watershed and Melioration Asset Management**.

## What has actually been implemented
- Asset-priority scoring prototype with deterministic rule tests.
- WNTR hydraulic demonstration **script prepared, not yet executed or calibrated**.
- Synthetic ablation experiments and BattLeDIM external validation were performed separately in the research work and are **not** proof of full digital-twin deployment.

## Scope limits
BattLeDIM is a simulated water-distribution network benchmark; it is not field oil-and-gas data and does not by itself validate watershed, drainage or irrigation operations. Uploaded CSV measurements alone have not established a verified network topology or sensor-to-asset mapping. Priority scores are illustrative, not observed maintenance outcomes.

## Run tests
```bash
python -m pytest water_twin/tests -q
```

## Next research milestone
Acquire verified network topology and sensor mapping, execute hydraulic simulation, compare measured-vs-simulated residuals with sensor-only baselines, and assess event localization and maintenance decision quality.
