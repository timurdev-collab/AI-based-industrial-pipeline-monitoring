# Executed hydraulic proxy demonstration (21 October 2026)

This is **not** a calibrated hydraulic network digital twin, not WNTR/EPANET and not BattLeDIM ground truth. It is a transparent educational two-pipe steady-state model using assumed demand and quadratic head-loss coefficients.

- Source: `water_twin/src/hydraulic_proxy.py`
- Data: `water_twin/results/hydraulic_proxy_results.csv`
- Leak sweep: 0 to 0.005 m³/s (six illustrative scenarios).
- Modeled service pressure: 34.088 m (no leak), 26.978 m (0.005 m³/s leak).
- The 7.11 m decrease is an output of assumed model parameters, **not an observed leak effect**.
- Locally executed four tests in 0.03 s for the same implementation logic.
- WNTR remained unavailable in the local runtime and no WNTR hydraulic simulation was executed.

## Reproduce
```bash
python -m pytest water_twin/tests/test_hydraulic_proxy.py -q
python -m water_twin.src.hydraulic_proxy
```

## Next publication milestone
Secure verified network topology and sensor mapping, use WNTR/EPANET, calibrate hydraulic parameters and compare residual-based alerts against event labels. This proxy alone provides **no statistical evidence** of improved fault detection, asset localization or maintenance outcomes.
