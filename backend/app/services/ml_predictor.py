import joblib
import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MLPredictor:
    def __init__(self):
        self.model = None

    def load_model(self, model_path: str):
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                logger.info(f"Loaded ML model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning(f"Model file not found at {model_path}. Prediction will be stubbed.")

    def predict_churn_risk(self, features: dict) -> float:
        """
        Predict churn risk for a single customer.
        Expects a dictionary of features matching the model's ColumnTransformer.
        """
        if self.model is None:
            # Fallback logic if model isn't trained yet
            return min(1.0, (features.get('days_since_last_login', 0) / 30) * 0.5 + 
                            (features.get('open_tickets', 0) * 0.2))

        try:
            import pandas as pd
            df = pd.DataFrame([features])
            
            # Predict probability of class 1 (churn)
            proba = self.model.predict_proba(df)[0][1]
            return float(proba)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return 0.5

predictor = MLPredictor()
