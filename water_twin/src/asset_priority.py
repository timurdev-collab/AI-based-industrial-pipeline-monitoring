"""Illustrative water-asset maintenance-priority score (not calibrated)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AssetSignal:
    anomaly_probability: float
    consequence: float
    vulnerability: float
    uncertainty: float = 0.0

def priority_score(signal: AssetSignal) -> float:
    """Score in [0,1]; illustrative, not a validated failure-risk probability."""
    for name in ("anomaly_probability", "consequence", "vulnerability", "uncertainty"):
        value = getattr(signal, name)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be a number in [0,1]")
    return round(
        0.4 * signal.anomaly_probability +
        0.3 * signal.consequence +
        0.2 * signal.vulnerability +
        0.1 * signal.uncertainty,
        6,
    )
