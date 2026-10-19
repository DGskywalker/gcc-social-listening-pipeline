"""
Unit tests for Validation Metrics and Gold Dataset integrity.
"""

from pathlib import Path
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, cohen_kappa_score

BASE_DIR = Path(__file__).resolve().parent.parent
GOLD_DATASET_PATH = BASE_DIR / "data" / "gold_dataset_150.csv"


def test_gold_dataset_integrity():
    assert GOLD_DATASET_PATH.exists(), "Gold dataset must exist at data/gold_dataset_150.csv"
    df = pd.read_csv(GOLD_DATASET_PATH)

    # Verify exactly 150 gold records
    assert len(df) == 150, f"Expected 150 gold items, found {len(df)}"

    required_cols = [
        "post_id", "platform", "text", "language", "brand",
        "gold_sentiment", "gold_theme", "is_sarcasm", "dialect", "annotator_notes"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"

    # Verify valid sentiment categories
    valid_sentiments = {"positive", "negative", "neutral"}
    assert set(df["gold_sentiment"].unique()).issubset(valid_sentiments)

    # Verify all 5 benchmark brands are represented
    expected_brands = {"Al-Noor Telecom", "DesertPay", "Oasis Retail", "Falcon Ride", "GulfCloud"}
    assert set(df["brand"].unique()) == expected_brands

    # Verify sarcasm items exist
    assert df["is_sarcasm"].sum() >= 5


def test_metrics_calculation_functions():
    y_true = ["positive", "negative", "neutral", "negative", "positive"]
    y_pred = ["positive", "negative", "neutral", "positive", "positive"]

    acc = accuracy_score(y_true, y_pred)
    assert acc == 0.8  # 4 out of 5 correct

    kappa = cohen_kappa_score(y_true, y_pred)
    assert isinstance(kappa, float)
    assert -1.0 <= kappa <= 1.0

    p, r, f1, sup = precision_recall_fscore_support(y_true, y_pred, average="macro")
    assert isinstance(f1, float)
