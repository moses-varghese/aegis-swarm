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

print("Generating normal flight data...")
print("Generating labeled anomaly data...")
df_normal = generate_normal_data()
df_normal['anomaly_type'] = 'Normal'

df_anomalies = generate_labeled_anomalies()
df_combined = pd.concat([df_normal, df_anomalies], ignore_index=True)

features = ['lat', 'lon', 'altitude', 'battery_level']
labels = df_combined['anomaly_type']
data = df_combined[features].values

# --- 2. Data Scaling ---
print("Scaling data...")
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)
joblib.dump(scaler, os.path.join(OUTPUT_DIR, 'scaler.pkl'))
print(f"Scaler saved to {OUTPUT_DIR}/scaler.pkl")

# --- 3. PyTorch DataLoader ---
tensor_data = torch.FloatTensor(data_scaled)
dataset = TensorDataset(tensor_data, tensor_data)
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

print("Training RandomForestClassifier...")
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(data_scaled, labels)

# Save the trained classifier
classifier_path = os.path.join(OUTPUT_DIR, 'classifier.pkl')
joblib.dump(classifier, classifier_path)
print(f"Classifier saved to {classifier_path}")

# --- 4. Model Training ---
print("Training Autoencoder model...")
model = Autoencoder()
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

num_epochs = 20
for epoch in range(num_epochs):
    for data_batch, _ in data_loader:
        recon = model(data_batch)
        loss = criterion(recon, data_batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.6f}')

torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, 'autoencoder.pth'))
print(f"Model trained and saved to {OUTPUT_DIR}/autoencoder.pth")

# --- 5. Determine Anomaly Threshold ---
print("Determining anomaly threshold...")
reconstruction_errors = []
with torch.no_grad():
    for data_batch, _ in data_loader:
        recon = model(data_batch)
        loss = torch.mean((data_batch - recon) ** 2, dim=1)
        reconstruction_errors.extend(loss.numpy())

threshold = np.max(reconstruction_errors) * 1.2
print(f"Calculated anomaly threshold: {threshold}")
with open(os.path.join(OUTPUT_DIR, "threshold.txt"), "w") as f:
    f.write(str(threshold))
print(f"Threshold saved to {OUTPUT_DIR}/threshold.txt")