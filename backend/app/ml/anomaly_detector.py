import torch
import joblib
import numpy as np
from .model import Autoencoder
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self, model_path='autoencoder.pth', scaler_path='scaler.pkl', threshold_path='threshold.txt', classifier_path='classifier.pkl'):
        # Load the trained model
        logger.info("Initializing AnomalyDetector...")
        try:
            # Construct file paths
            base_path = "app/ml/"
            model_file = f"{base_path}{model_path}"
            scaler_file = f"{base_path}{scaler_path}"
            threshold_file = f"{base_path}{threshold_path}"
            classifier_file = f"{base_path}{classifier_path}"

            
            # Load the Autoencoder model
            self.model = Autoencoder()
            self.model.load_state_dict(torch.load(model_file))
            self.model.eval()
            logger.info("Autoencoder model loaded successfully.", extra={'path': model_file})
            self.classifier = joblib.load(classifier_file)
            logger.info("Classifier model loaded successfully.", extra={'path': classifier_file})
            # Load the scaler
            self.scaler = joblib.load(scaler_file)
            logger.info("Scaler loaded successfully.", extra={'path': scaler_file})
        
            # Load the pre-calculated threshold
            with open(threshold_file, "r") as f:
                self.threshold = float(f.read())
            logger.info(f"Anomaly threshold loaded: {self.threshold}", extra={'path': threshold_file, 'threshold': self.threshold})
            logger.info("AnomalyDetector initialized successfully with all components.")
        except FileNotFoundError as e:
            logger.critical(f"A required model file was not found: {e.filename}. The application cannot start.", exc_info=True)
            # Re-raise the exception to crash the application, as it cannot function without the models.
            raise
        except Exception:
            logger.critical("An unexpected error occurred during AnomalyDetector initialization.", exc_info=True)
            raise

    def predict(self, telemetry: dict, drone_id: str) -> dict:
        """
        Predicts if a given telemetry data point is an anomaly.
        """
        # Extract features in the correct order
        try:
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

            anomaly_type = "None"
            # --- Step 2: If anomaly is detected, classify its type ---
            if is_anomaly:
                prediction = self.classifier.predict(data_scaled)
                anomaly_type = prediction[0]
                logger.info(
                        "Anomaly detected and classified.", 
                        extra={'drone_id': drone_id, 'anomaly_type': anomaly_type, 'reconstruction_error': error}
                    )
            
            result = {
                    "is_anomaly": is_anomaly,
                    "reconstruction_error": error,
                    "threshold": self.threshold,
                    "anomaly_type": anomaly_type
                }

            logger.debug("Prediction finished.", extra={'drone_id': drone_id, 'result': result})
            
            return result
            
        except KeyError as e:
            logger.error(f"Missing expected key in telemetry data: {e}", extra={'drone_id': drone_id}, exc_info=True)
            # Return a default non-anomalous result to prevent crashes
            return {"is_anomaly": False, "reconstruction_error": 0, "threshold": self.threshold, "anomaly_type": "Data Error"}