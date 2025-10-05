import torch
from torch import nn

# We will use 4 features: lat, lon, altitude, battery_level
INPUT_DIM = 4

class Autoencoder(nn.Module):
    """
    A simple Autoencoder model for anomaly detection.
    The architecture compresses the input data and then tries
    to reconstruct it. A high reconstruction error indicates an anomaly.
    """
    def __init__(self):
        super(Autoencoder, self).__init__()
        # Encoder: Compresses the input
        self.encoder = nn.Sequential(
            nn.Linear(INPUT_DIM, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        # Decoder: Reconstructs the input from the compressed representation
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, INPUT_DIM),
            nn.Sigmoid()  # Use Sigmoid for the final layer as data will be scaled between 0 and 1
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded