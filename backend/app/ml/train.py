import torch
import pandas as pd
import joblib
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from torch.utils.data import DataLoader, TensorDataset
from model import Autoencoder
import random
import numpy as np
from pythonjsonlogger import jsonlogger
import logging


# --- Structured Logging Configuration ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


# --- Define the output directory ---
OUTPUT_DIR = "app/ml"
os.makedirs(OUTPUT_DIR, exist_ok=True) # Ensure the directory exists

# --- 1. Data Generation ---
def generate_normal_data(num_samples=5000):
    data = []
    lat, lon, alt, battery = 8.5241, 76.9366, 100.0, 100.0
    for _ in range(num_samples):
        lat += random.uniform(-0.0001, 0.0001)
        lon += random.uniform(-0.0001, 0.0001)
        alt += random.uniform(-1, 1)
        battery -= 0.01
        data.append([lat, lon, alt, battery])
    return pd.DataFrame(data, columns=['lat', 'lon', 'altitude', 'battery_level'])

# --- NEW: Labeled Anomaly Data Generation ---
def generate_labeled_anomalies(num_samples_per_type=2500):
    """Generates a DataFrame of labeled anomalous data."""
    anomalies = []
    
    # Type 1: GPS Spoofing (erratic, large jumps in location)
    for _ in range(num_samples_per_type):
        anomalies.append([
            8.5241 + random.uniform(-0.5, 0.5), # Large lat jump
            76.9366 + random.uniform(-0.5, 0.5), # Large lon jump
            100.0 + random.uniform(-10, 10),
            90.0 - random.uniform(0, 5),
            "GPS Spoofing" # Label
        ])
        
    # Type 2: Rapid Battery Drain (sudden, sharp drops in battery)
    for _ in range(num_samples_per_type):
        anomalies.append([
            8.5241 + random.uniform(-0.0001, 0.0001),
            76.9366 + random.uniform(-0.0001, 0.0001),
            100.0 + random.uniform(-1, 1),
            80.0 - random.uniform(10, 20), # Rapid drain
            "Rapid Battery Drain" # Label
        ])
    
    columns = ['lat', 'lon', 'altitude', 'battery_level', 'anomaly_type']
    return pd.DataFrame(anomalies, columns=columns)

# print("Generating normal flight data...")
# df = generate_normal_data()
# features = ['lat', 'lon', 'altitude', 'battery_level']
# data = df[features].values

logger.info("Starting the model training process.")

logger.info("Generating normal and anomalous flight data...")
df_normal = generate_normal_data()
df_normal['anomaly_type'] = 'Normal'

df_anomalies = generate_labeled_anomalies()
df_combined = pd.concat([df_normal, df_anomalies], ignore_index=True)
logger.info(f"Data generation complete. Total samples: {len(df_combined)}")

features = ['lat', 'lon', 'altitude', 'battery_level']
labels = df_combined['anomaly_type']
data = df_combined[features].values

logger.info("Scaling data...")

# --- 2. Data Scaling ---
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)
scaler_path = os.path.join(OUTPUT_DIR, 'scaler.pkl')
joblib.dump(scaler, scaler_path)
logger.info(f"Scaler saved successfully.", extra={'path': scaler_path})

logger.info("Training RandomForestClassifier...")
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(data_scaled, labels)
classifier_path = os.path.join(OUTPUT_DIR, 'classifier.pkl')
joblib.dump(classifier, classifier_path)
logger.info(f"Classifier trained and saved successfully.", extra={'path': classifier_path})

logger.info("Preparing data for Autoencoder training...")
# --- 3. PyTorch DataLoader ---
tensor_data = torch.FloatTensor(data_scaled)
dataset = TensorDataset(tensor_data, tensor_data)
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# --- 4. Model Training ---
logger.info("Training Autoencoder model...")
model = Autoencoder()
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

num_epochs = 20
for epoch in range(num_epochs):
    epoch_loss = 0.0
    for data_batch, _ in data_loader:
        recon = model(data_batch)
        loss = criterion(recon, data_batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    logger.info(f"Autoencoder training progress.", extra={'epoch': epoch + 1, 'total_epochs': num_epochs, 'Loss': round(loss.item(), 6), 'average_loss': epoch_loss / len(data_loader)})
autoencoder_path = os.path.join(OUTPUT_DIR, 'autoencoder.pth')
torch.save(model.state_dict(), autoencoder_path)
logger.info(f"Autoencoder trained and saved successfully.", extra={'path': autoencoder_path})

# --- 5. Determine Anomaly Threshold ---
logger.info("Determining anomaly threshold...")
reconstruction_errors = []
with torch.no_grad():
    for data_batch, _ in data_loader:
        recon = model(data_batch)
        loss = torch.mean((data_batch - recon) ** 2, dim=1)
        reconstruction_errors.extend(loss.numpy())

threshold = np.max(reconstruction_errors) * 1.2
threshold_path = os.path.join(OUTPUT_DIR, "threshold.txt")
with open(threshold_path, "w") as f:
    f.write(str(threshold))
logger.info(f"Anomaly threshold calculated and saved.", extra={'threshold': threshold, 'path': threshold_path})
logger.info("Model training process completed successfully.")