"""Reproducible SCADA benchmark: leakage-safe chronological evaluation.

Usage: python research_pipeline.py --csv /path/to/scada_pipeline.csv --out results
The original Kaggle notebook is intentionally preserved.
"""
from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

LOG = logging.getLogger("scada_benchmark")
FEATURES = ("pressure", "flow_rate", "temperature")
REQUIRED = (*FEATURES, "target")


def load_data(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"SCADA dataset missing: {path}. Download from the documented Kaggle source.")
    frame = pd.read_csv(path)
    missing = sorted(set(REQUIRED).difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for name in FEATURES:
        frame[name] = pd.to_numeric(frame[name], errors="coerce")
    if frame[list(FEATURES)].notna().sum().min() == 0:
        raise ValueError("At least one sensor feature has no valid numeric readings")
    labels = pd.to_numeric(frame["target"], errors="raise")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("target must contain only binary labels 0 and 1")
    frame["target"] = labels.astype(int)
    if "timestamp" in frame.columns:
        parsed = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
        if parsed.notna().all():
            frame = frame.assign(_time=parsed).sort_values("_time", kind="stable").drop(columns="_time")
        else:
            LOG.warning("Unparseable timestamps; preserving file order")
    return frame.reset_index(drop=True)


def chronological_split(frame: pd.DataFrame, train_fraction: float = .6,
                        validation_fraction: float = .2):
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1 - train_fraction:
        raise ValueError("Invalid partition fractions")
    n = len(frame)
    a, b = int(n * train_fraction), int(n * (train_fraction + validation_fraction))
    if a < 20 or b-a < 10 or n-b < 10:
        raise ValueError("Insufficient observations for chronological partitions")
    return frame.iloc[:a].copy(), frame.iloc[a:b].copy(), frame.iloc[b:].copy()


def make_windows(values: np.ndarray, labels: np.ndarray, length: int):
    """Build windows inside a single partition; no observations cross partitions."""
    if length < 2 or len(values) < length:
        raise ValueError("Window length invalid for partition")
    windows = np.stack([values[i-length+1:i+1] for i in range(length-1, len(values))])
    return windows, labels[length-1:]


def evaluate(y, scores, threshold: float) -> dict:
    y = np.asarray(y).astype(int)
    scores = np.asarray(scores, dtype=float).reshape(-1)
    if len(y) != len(scores) or not np.isfinite(scores).all():
        raise ValueError("Invalid scores")
    pred = (scores >= threshold).astype(int)
    result = {
        "n": int(len(y)),
        "anomalies": int(y.sum()),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "average_precision": None,
        "roc_auc": None,
    }
    if len(np.unique(y)) == 2:
        result["average_precision"] = float(average_precision_score(y, scores))
        result["roc_auc"] = float(roc_auc_score(y, scores))
    return result


def select_threshold(y_validation, scores_validation) -> float:
    """Select on validation only; test labels are never used for optimization."""
    scores = np.asarray(scores_validation).reshape(-1)
    thresholds = np.unique(np.r_[scores, np.nextafter(scores.max(), np.inf)])
    f1s = [f1_score(y_validation, scores >= t, zero_division=0) for t in thresholds]
    return float(thresholds[int(np.argmax(f1s))])


def train_lstm(train_x, train_y, val_x, val_y, seed: int, epochs: int):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Install optional TensorFlow dependency for --lstm") from exc
    tf.keras.utils.set_random_seed(seed)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=train_x.shape[1:]),
        tf.keras.layers.LSTM(50),
        tf.keras.layers.Dropout(.2),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy")
    callbacks = [tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True)]
    counts = np.bincount(train_y.astype(int), minlength=2)
    weights = {cls: float(len(train_y) / (2 * count))
               for cls, count in enumerate(counts) if count > 0}
    model.fit(train_x, train_y, validation_data=(val_x, val_y),
              epochs=epochs, batch_size=32, shuffle=False,
              class_weight=weights, callbacks=callbacks, verbose=0)
    return model


def run(csv: Path, out: Path, length: int = 10, seed: int = 42,
        lstm: bool = False, epochs: int = 30) -> dict:
    random.seed(seed)
    np.random.seed(seed)
    frame = load_data(csv)
    train, val, test = chronological_split(frame)
    # Fit both imputation and scaling ONLY on the training partition.
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(train[list(FEATURES)]))
    x_val = scaler.transform(imputer.transform(val[list(FEATURES)]))
    x_test = scaler.transform(imputer.transform(test[list(FEATURES)]))
    xtr, ytr = make_windows(x_train, train.target.to_numpy(), length)
    xva, yva = make_windows(x_val, val.target.to_numpy(), length)
    xte, yte = make_windows(x_test, test.target.to_numpy(), length)
    if len(np.unique(ytr)) < 2:
        raise ValueError("Training partition contains only one target class; choose independent scenario splits")
    tr_flat, va_flat, te_flat = (a.reshape(len(a), -1) for a in (xtr, xva, xte))
    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=200, min_samples_leaf=3, random_state=seed,
            class_weight="balanced_subsample", n_jobs=-1),
        "isolation_forest": IsolationForest(
            n_estimators=200, random_state=seed, contamination="auto", n_jobs=-1),
    }
    out.mkdir(parents=True, exist_ok=True)
    results = {"dataset": str(csv), "records": len(frame), "window_length": length,
               "split_rows": [len(train), len(val), len(test)],
               "window_counts": [len(ytr), len(yva), len(yte)],
               "seed": seed, "models": {}}
    for name, model in models.items():
        model.fit(tr_flat if name == "isolation_forest" else tr_flat,
                  **({} if name == "isolation_forest" else {"y": ytr}))
        score_fn = (lambda x: -model.decision_function(x)) if name == "isolation_forest" else (
            lambda x: model.predict_proba(x)[:, list(model.classes_).index(1)])
        sv, st = score_fn(va_flat), score_fn(te_flat)
        threshold = select_threshold(yva, sv)
        results["models"][name] = {"threshold": threshold, **evaluate(yte, st, threshold)}
    if lstm:
        model = train_lstm(xtr, ytr, xva, yva, seed=seed, epochs=epochs)
        sv = model.predict(xva, verbose=0).reshape(-1)
        st = model.predict(xte, verbose=0).reshape(-1)
        threshold = select_threshold(yva, sv)
        results["models"]["lstm"] = {"threshold": threshold, **evaluate(yte, st, threshold)}
        model.save(out / "lstm.keras")
    (out / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    LOG.info("Wrote %s", out / "metrics.json")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--window", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lstm", action="store_true")
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(args.csv, args.out, args.window, args.seed, args.lstm, args.epochs)


if __name__ == "__main__":
    main()
