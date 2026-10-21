# Research implementation and evidence roadmap

## Research objective
Study whether hydraulic simulation combined with sensor anomaly detection improves asset-specific fault interpretation and maintenance prioritization in water distribution, irrigation and drainage networks.

## Experimental separation
1. **Completed existing work:** synthetic SCADA-style model ablations and separate BattLeDIM 2018/2019 sensor-only external evaluation.
2. **New software prototype:** deterministic asset priority rule; its values are illustrative.
3. **Planned verification:** execute a hydraulic benchmark, obtain network INP / verified topology and sensor mapping, calibrate model, extract residuals, compare sensor-only, hydraulic-only and fusion approaches.

## Required evaluation
Report event-level recall and detection delay, false alarms per day, localization top-k accuracy, calibrated uncertainty, sensitivity to topology error, and maintenance-ranking utility against an explicit ground truth. Use time-/network-disjoint partitions where feasible.

## Research-integrity statement
Do not call the asset score a real failure probability, do not claim a calibrated digital twin, and do not equate BattLeDIM's virtual hydraulic model with real operational SCADA without qualifications.
