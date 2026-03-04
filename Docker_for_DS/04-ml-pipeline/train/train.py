"""
ML Training Script.

Trains a classifier on the Iris dataset (as a representative example),
saves the model and metadata to the /app/models directory.

Usage inside container:
    python train.py

The /app/models directory should be a bind mount so artifacts persist
on the host machine after the container exits.
"""

import json
import logging
import os
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Configure logging to stdout (captured by docker logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ============================================================
# Configuration
# ============================================================
MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))
RANDOM_STATE = int(os.environ.get("RANDOM_STATE", "42"))
N_ESTIMATORS = int(os.environ.get("N_ESTIMATORS", "100"))
MAX_DEPTH = int(os.environ.get("MAX_DEPTH", "5"))
TEST_SIZE = float(os.environ.get("TEST_SIZE", "0.2"))
CV_FOLDS = int(os.environ.get("CV_FOLDS", "5"))


def build_pipeline() -> Pipeline:
    """Build the sklearn Pipeline (preprocessor + model)."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE,
        )),
    ])


def save_artifact(obj: Any, path: Path) -> None:
    """Serialize an object to a pickle file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    log.info("Saved artifact: %s (%.1f KB)", path, path.stat().st_size / 1024)


def save_json(data: dict, path: Path) -> None:
    """Write a dict to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log.info("Saved JSON: %s", path)


def main() -> None:
    """Train model and save artifacts."""
    log.info("Starting training run")
    log.info("Config: n_estimators=%d, max_depth=%d, test_size=%.1f",
             N_ESTIMATORS, MAX_DEPTH, TEST_SIZE)

    # ----------------------------------------------------------
    # Load data
    # ----------------------------------------------------------
    iris = load_iris(as_frame=True)
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names.tolist()
    target_names = iris.target_names.tolist()

    log.info("Dataset: %d samples, %d features, %d classes",
             len(X), X.shape[1], len(target_names))

    # ----------------------------------------------------------
    # Split
    # ----------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    log.info("Train: %d samples | Test: %d samples", len(X_train), len(X_test))

    # ----------------------------------------------------------
    # Train
    # ----------------------------------------------------------
    pipeline = build_pipeline()
    log.info("Training pipeline...")
    pipeline.fit(X_train, y_train)
    log.info("Training complete")

    # ----------------------------------------------------------
    # Evaluate
    # ----------------------------------------------------------
    y_pred = pipeline.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)

    # Cross-validation on full dataset
    cv_scores = cross_val_score(pipeline, X, y, cv=CV_FOLDS, scoring="accuracy")

    log.info("Test accuracy  : %.4f", test_accuracy)
    log.info("CV accuracy    : %.4f +/- %.4f", cv_scores.mean(), cv_scores.std())

    report = classification_report(
        y_test, y_pred, target_names=target_names, output_dict=True
    )

    # ----------------------------------------------------------
    # Save artifacts
    # ----------------------------------------------------------
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Model
    model_path = MODELS_DIR / "model.pkl"
    save_artifact(pipeline, model_path)

    # Metadata for the serving container
    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_names": feature_names,
        "target_names": target_names,
        "n_features": X.shape[1],
        "n_classes": len(target_names),
        "hyperparameters": {
            "n_estimators": N_ESTIMATORS,
            "max_depth": MAX_DEPTH,
            "random_state": RANDOM_STATE,
        },
    }
    save_json(metadata, MODELS_DIR / "metadata.json")

    # Training report
    training_report = {
        "test_accuracy": float(test_accuracy),
        "cv_mean_accuracy": float(cv_scores.mean()),
        "cv_std_accuracy": float(cv_scores.std()),
        "cv_scores": cv_scores.tolist(),
        "classification_report": report,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
    }
    save_json(training_report, MODELS_DIR / "training_report.json")

    log.info("All artifacts saved to: %s", MODELS_DIR)
    log.info("Training run complete. Test accuracy: %.4f", test_accuracy)


if __name__ == "__main__":
    main()
