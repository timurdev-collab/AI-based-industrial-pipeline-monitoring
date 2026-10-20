# Research reproducibility and remediation

## Source and limits
Original experiment: `AI Driven Pipeline Digital Twin.ipynb`.
The notebook loads `/kaggle/input/datasets/zara2099/scada-pipeline-operations-dataset/scada_pipeline.csv`. The repository does not contain the CSV. Dataset origin, simulation methodology, timestamps, licensing, grouping and physical representativeness must be verified independently. Notebook outputs are **not** a reproduced benchmark.

## Corrected implementation
`research_pipeline.py` is an independent, testable benchmark. It does not alter the original notebook. It:
- parses and validates the CSV schema
- preserves chronological order (sorts parseable timestamps)
- splits rows before fitting any imputer or scaler
- builds disjoint time windows **within each partition**
- uses supervised Random Forest and unsupervised Isolation Forest baselines
- optionally trains an LSTM with a **single sigmoid output** and training-derived class weights
- selects anomaly thresholds on validation data only
- reports test-set precision, recall, F1, average precision, ROC-AUC and confusion matrices
- refuses to train a supervised classifier if the training partition contains one class only

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-research.txt
# Optional for LSTM:
pip install 'tensorflow>=2.16,<3'
pytest -q tests/test_research_pipeline.py
python research_pipeline.py --csv /absolute/path/to/scada_pipeline.csv --out results
python research_pipeline.py --csv /absolute/path/to/scada_pipeline.csv --out results-lstm --lstm
```

Outputs: `metrics.json` and optional `lstm.keras`. Run and retain dataset checksum, Python/library versions, hardware, split indices and git SHA alongside results before citing them in a dissertation.

## Remaining scientific limitations
1. Chronological partitions are an improvement, not proof of independence. If multiple segments overlap in time, partition by **independent scenario / segment**, keeping complete fault events in one partition. Run-group labels need dataset inspection.
2. Timestamp interval is unknown. Window length 10 means ten samples, **not ten minutes** unless sampling is one minute.
3. No test-time class rebalancing. Class weighting changes loss contributions only.
4. No simulator calibration, physical digital twin or empirical pipeline performance can be inferred from these code changes.
5. No held-out scenario generalization, hyperparameter ablation or repeated-seed statistical inference has yet been executed.
6. Never claim validation scores from the original Kaggle notebook have been independently reproduced.
7. Verify the CSV license and whether it is physically measured or synthetic before redistribution.
