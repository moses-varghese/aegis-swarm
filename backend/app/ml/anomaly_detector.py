import torch
import joblib
import numpy as np
from .model import Autoencoder

class AnomalyDetector:
    def __init__(self, model_path='autoencoder.pth', scaler_path='scaler.pkl', threshold_path='threshold.txt'):
        # Load the trained model
        self.model = Autoencoder()
        # The model was trained in the 'ml' directory, so adjust path if needed
        model_file = f"app/ml/{model_path}"
        scaler_file = f"app/ml/{scaler_path}"
        threshold_file = f"app/ml/{threshold_path}"
        
        self.model.load_state_dict(torch.load(model_file))
        self.model.eval()
        
        # Load the scaler
        self.scaler = joblib.load(scaler_file)
        
        # Load the pre-calculated threshold
        with open(threshold_file, "r") as f:
            self.threshold = float(f.read())
        
        print("AnomalyDetector initialized with model, scaler, and threshold.")

    def predict(self, telemetry: dict) -> dict:
        """
        Predicts if a given telemetry data point is an anomaly.
        """
        # Extract features in the correct order
        features = [
            telemetry['location']['lat'],
            telemetry['location']['lon'],
            telemetry['location']['altitude'],
            telemetry['battery_level']
        ]
        
        data = np.array(features).reshape(1, -1)
        
        # Scale the data
        data_scaled = self.scaler.transform(data)
        tensor_data = torch.FloatTensor(data_scaled)
        
        # Get model reconstruction
        with torch.no_grad():
            reconstruction = self.model(tensor_data)
            error = torch.mean((tensor_data - reconstruction) ** 2).item()
            
        is_anomaly = error > self.threshold
        
        return {
            "is_anomaly": is_anomaly,
            "reconstruction_error": error,
            "threshold": self.threshold
        }