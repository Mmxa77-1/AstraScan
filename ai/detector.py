# ai/detector.py

import numpy as np
from sklearn.ensemble import RandomForestClassifier

class AIDetector:
    def __init__(self, use_ml=True):
        """
        AI vulnerability detector.
        use_ml: If True, train a RandomForest model; otherwise, use heuristic scoring.
        """
        self.use_ml = use_ml
        self.model = None
        self.training_data = []
        self.training_labels = []

    def add_training_sample(self, features, label=1):
        """
        Store training samples.
        label: default 1 (vulnerable), for unsupervised or heuristic you can ignore.
        """
        self.training_data.append(features)
        self.training_labels.append(label)

    def train_model(self):
        """
        Train RandomForestClassifier if enough samples exist.
        Returns (success: bool, message: str)
        """
        if not self.use_ml:
            return False, "ML disabled"

        if len(self.training_data) < 5:
            return False, "Not enough samples"

        try:
            X = np.array(self.training_data)
            y = np.array(self.training_labels)
            self.model = RandomForestClassifier(n_estimators=50)
            self.model.fit(X, y)
            return True, "Model trained"
        except Exception as e:
            return False, f"Training failed: {e}"

    def score(self, features):
        """
        Score a feature vector:
        - If ML model is trained: predict probability
        - Otherwise: simple heuristic (sum of features)
        """
        if self.model is None or not self.use_ml:
            return float(sum(features)) / (len(features) + 1)

        try:
            features = np.array(features).reshape(1, -1)
            prediction = self.model.predict_proba(features)[0][1]
            return float(prediction)
        except Exception:
            return 0.0


def extract_features(url, html, params):
    """
    Convert a page into a numeric feature vector.
    Simple demo features:
    - URL length
    - Number of GET/form parameters
    - HTML length
    - Contains keywords: login, id=, admin
    """
    url_len = len(url)
    param_count = len(params)
    html_len = len(html) if html else 0

    features = [
        url_len,
        param_count,
        html_len,
        int("login" in url.lower()),
        int("id=" in url.lower()),
        int("admin" in url.lower())
    ]

    return features
