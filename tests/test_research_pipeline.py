import numpy as np
import pandas as pd
import pytest

from research_pipeline import chronological_split, evaluate, load_data, make_windows, select_threshold


def test_chronological_boundaries_are_disjoint():
    frame = pd.DataFrame({"index": range(100)})
    a, b, c = chronological_split(frame)
    assert len(a) + len(b) + len(c) == 100
    assert a["index"].max() < b["index"].min() < c["index"].min()


def test_windows_preserve_partition_boundaries():
    x = np.arange(20, dtype=float).reshape(-1, 1)
    y = np.zeros(20, dtype=int)
    windows, labels = make_windows(x, y, 5)
    assert windows.shape == (16, 5, 1)
    assert np.array_equal(windows[0, :, 0], np.arange(5))
    assert np.array_equal(windows[-1, :, 0], np.arange(15, 20))
    assert len(labels) == 16


def test_validation_threshold_finds_separable_labels():
    y = np.array([0, 0, 1, 1])
    score = np.array([.1, .2, .8, .9])
    threshold = select_threshold(y, score)
    assert evaluate(y, score, threshold)["f1"] == 1.0


def test_single_class_metric_is_explicit():
    result = evaluate([0, 0], [0.2, 0.3], 0.5)
    assert result["roc_auc"] is None
    assert result["average_precision"] is None


def test_missing_required_features_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"pressure": [1], "target": [0]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Missing required"):
        load_data(path)


def test_missing_csv_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "missing.csv")


def test_nonbinary_labels_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"pressure": [1], "flow_rate": [2],
                  "temperature": [3], "target": [2]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="binary"):
        load_data(path)
