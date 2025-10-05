import torch
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from model import Autoencoder, INPUT_DIM
import random
import numpy as np

# --- 1. Data Generation ---
def generate_normal_data(num_samples=5000):
    """
    Generates a DataFrame of normal drone telemetry data.
    """
    data = []
    lat, lon, alt, battery = 8.5241, 76.9366, 100.0, 100.0
    for _ in range(num_samples):
        lat += random.uniform(-0.0001, 0.0001)
        lon += random.uniform(-0.0001, 0.0001)
        alt += random.uniform(-1, 1)
        battery -= 0.01
        data.append([lat, lon, alt, battery])
    return pd.DataFrame(data, columns=['lat', 'lon', 'altitude', 'battery_level'])

print("Generating normal flight data...")
df = generate_normal_data()
features = ['lat', 'lon', 'altitude', 'battery_level']
data = df[features].values

# --- 2. Data Scaling ---
print("Scaling data...")
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)
# Save the scaler for later use in inference
joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved to scaler.pkl")

# --- 3. PyTorch DataLoader ---
tensor_data = torch.FloatTensor(data_scaled)
dataset = TensorDataset(tensor_data, tensor_data) # Input and target are the same
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# --- 4. Model Training ---
print("Training Autoencoder model...")
model = Autoencoder()
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

num_epochs = 20
for epoch in range(num_epochs):
    for data_batch, _ in data_loader:
        # Forward pass
        recon = model(data_batch)
        loss = criterion(recon, data_batch)
        
        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.6f}')

# Save the trained model
torch.save(model.state_dict(), 'autoencoder.pth')
print("Model trained and saved to autoencoder.pth")

# --- 5. Determine Anomaly Threshold ---
print("Determining anomaly threshold...")
reconstruction_errors = []
with torch.no_grad():
    for data_batch, _ in data_loader:
        recon = model(data_batch)
        loss = torch.mean((data_batch - recon) ** 2, dim=1)
        reconstruction_errors.extend(loss.numpy())

# Set threshold to be a value slightly higher than the max reconstruction error on normal data
threshold = np.max(reconstruction_errors) * 1.2 
print(f"Calculated anomaly threshold: {threshold}")
# Save the threshold
with open("threshold.txt", "w") as f:
    f.write(str(threshold))
print("Threshold saved to threshold.txt")