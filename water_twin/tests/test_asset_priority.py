from water_twin.src.asset_priority import AssetSignal, priority_score

def test_score_bounds():
    assert priority_score(AssetSignal(0, 0, 0, 0)) == 0
    assert priority_score(AssetSignal(1, 1, 1, 1)) == 1

def test_anomaly_monotonicity():
    low = priority_score(AssetSignal(.1, .5, .5))
    high = priority_score(AssetSignal(.9, .5, .5))
    assert high > low

def test_invalid_probability():
    try:
        priority_score(AssetSignal(1.2, .2, .2))
    except ValueError:
        return
    raise AssertionError("out-of-range input must raise ValueError")
