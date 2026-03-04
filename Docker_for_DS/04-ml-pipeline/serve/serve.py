"""
Prediction API Server.

Flask REST API that loads a trained sklearn model and serves predictions.
The model file is loaded from the /app/models volume (shared with training container).

Endpoints:
    GET  /health          -- Health check
    GET  /info            -- Model metadata
    POST /predict         -- Single prediction
    POST /predict/batch   -- Batch predictions
"""

import json
import logging
import os
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from flask import Flask, Response, jsonify, request

# ============================================================
# Configuration
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))
MODEL_PATH = MODELS_DIR / "model.pkl"
METADATA_PATH = MODELS_DIR / "metadata.json"
PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__)

# ============================================================
# Model loading (lazy -- loaded once on first request)
# ============================================================
_model: Any = None
_metadata: dict = {}


def load_model() -> tuple[Any, dict]:
    """Load model and metadata from disk. Cache in module-level variables."""
    global _model, _metadata

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run the training container first."
            )
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        log.info("Model loaded from %s", MODEL_PATH)

    if not _metadata:
        if METADATA_PATH.exists():
            with open(METADATA_PATH, encoding="utf-8") as f:
                _metadata = json.load(f)
            log.info("Metadata loaded from %s", METADATA_PATH)

    return _model, _metadata


# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
def health() -> Response:
    """Health check endpoint. Returns 200 if model is loadable."""
    try:
        load_model()
        return jsonify({"status": "healthy", "model_loaded": True})
    except FileNotFoundError as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.get("/info")
def info() -> Response:
    """Return model metadata (features, classes, training config)."""
    try:
        _, metadata = load_model()
        return jsonify(metadata)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503


@app.post("/predict")
def predict() -> Response:
    """
    Single prediction endpoint.

    Request body (JSON):
        {
            "features": [5.1, 3.5, 1.4, 0.2]
        }

    Response (JSON):
        {
            "prediction": 0,
            "prediction_label": "setosa",
            "probabilities": {"setosa": 0.97, "versicolor": 0.02, "virginica": 0.01}
        }
    """
    try:
        model, metadata = load_model()
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    features = data.get("features")
    if features is None:
        return jsonify({"error": "Missing 'features' key in request body"}), 400

    n_expected = metadata.get("n_features", None)
    if n_expected is not None and len(features) != n_expected:
        return jsonify({
            "error": f"Expected {n_expected} features, got {len(features)}"
        }), 400

    try:
        X = np.array(features, dtype=float).reshape(1, -1)
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Could not parse features: {e}"}), 400

    prediction = int(model.predict(X)[0])
    target_names = metadata.get("target_names", [])
    label = target_names[prediction] if prediction < len(target_names) else str(prediction)

    probabilities = {}
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
        probabilities = {
            name: round(float(p), 4)
            for name, p in zip(target_names or range(len(probs)), probs)
        }

    log.info("Prediction: %s (%d) for features %s", label, prediction, features)

    return jsonify({
        "prediction": prediction,
        "prediction_label": label,
        "probabilities": probabilities,
    })


@app.post("/predict/batch")
def predict_batch() -> Response:
    """
    Batch prediction endpoint.

    Request body (JSON):
        {
            "instances": [
                [5.1, 3.5, 1.4, 0.2],
                [6.7, 3.0, 5.2, 2.3]
            ]
        }

    Response (JSON):
        {
            "predictions": [
                {"prediction": 0, "prediction_label": "setosa"},
                {"prediction": 2, "prediction_label": "virginica"}
            ],
            "count": 2
        }
    """
    try:
        model, metadata = load_model()
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    instances = data.get("instances")
    if instances is None:
        return jsonify({"error": "Missing 'instances' key in request body"}), 400

    if not isinstance(instances, list) or len(instances) == 0:
        return jsonify({"error": "'instances' must be a non-empty list"}), 400

    try:
        X = np.array(instances, dtype=float)
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Could not parse instances: {e}"}), 400

    target_names = metadata.get("target_names", [])
    raw_preds = model.predict(X)

    results = []
    for pred in raw_preds:
        pred_int = int(pred)
        label = target_names[pred_int] if pred_int < len(target_names) else str(pred_int)
        results.append({"prediction": pred_int, "prediction_label": label})

    return jsonify({"predictions": results, "count": len(results)})


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    log.info("Starting prediction server on port %d", PORT)
    log.info("Model path: %s", MODEL_PATH)
    app.run(host="0.0.0.0", port=PORT, debug=False)
