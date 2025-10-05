# import asyncio
# import websockets
# import json
# import random
# import uuid
# from datetime import datetime

# # The WebSocket URI of our backend server
# WEBSOCKET_URI = "ws://localhost:8000/ws/drone"

# class Drone:
#     """
#     Represents and simulates a single drone.
#     """
#     def __init__(self, drone_id):
#         self.id = drone_id
#         # Start at a realistic location (e.g., near Thiruvananthapuram)
#         self.lat = 8.5241
#         self.lon = 76.9366
#         self.altitude = 100.0  # in meters
#         self.battery = 100.0
#         self.status = "Active"

#     def simulate_movement(self):
#         """
#         Simulates the drone's movement and battery drain.
#         In a normal scenario, changes are small and consistent.
#         """
#         # Simulate slight random movement
#         self.lat += random.uniform(-0.0001, 0.0001)
#         self.lon += random.uniform(-0.0001, 0.0001)
        
#         # Simulate slight change in altitude
#         self.altitude += random.uniform(-1, 1)
#         if self.altitude < 50:
#             self.altitude = 50 # Don't go too low
        
#         # Simulate battery drain
#         self.battery -= 0.05
#         if self.battery < 0:
#             self.battery = 0
#             self.status = "Offline"

#     def get_telemetry(self) -> dict:
#         """
#         Generates the current telemetry data packet.
#         """
#         self.simulate_movement()
#         return {
#             "drone_id": str(self.id),
#             "timestamp": datetime.utcnow().isoformat(),
#             "location": {
#                 "lat": self.lat,
#                 "lon": self.lon,
#                 "altitude": self.altitude,
#             },
#             "battery_level": self.battery,
#             "status": self.status
#         }

# async def run_simulator():
#     """
#     Connects to the WebSocket server and sends telemetry data periodically.
#     """
#     drone_id = uuid.uuid4()
#     drone = Drone(drone_id)
    
#     print(f"🛰️ Drone Simulator started for Drone ID: {drone_id}")
    
#     async with websockets.connect(WEBSOCKET_URI) as websocket:
#         print(f"📡 Connected to backend at {WEBSOCKET_URI}")
#         while drone.status != "Offline":
#             telemetry_data = drone.get_telemetry()
#             await websocket.send(json.dumps(telemetry_data))
#             print(f"Sent telemetry: {telemetry_data}")
            
#             # Send data every 2 seconds
#             await asyncio.sleep(2)
#         print(f"Drone {drone_id} is offline. Simulator shutting down.")


# if __name__ == "__main__":
#     try:
#         asyncio.run(run_simulator())
#     except KeyboardInterrupt:
#         print("Simulator stopped by user.")
#     except ConnectionRefusedError:
#         print("Connection refused. Is the backend server running?")

import asyncio
import websockets
import json
import random
import uuid
from datetime import datetime

# WEBSOCKET_URI = "ws://localhost:8000/ws/drone"
WEBSOCKET_URI = "ws://backend:8000/ws/drone"

class Drone:
    def __init__(self, drone_id):
        self.id = drone_id
        self.lat = 8.5241 + random.uniform(-0.05, 0.05)
        self.lon = 76.9366 + random.uniform(-0.05, 0.05)
        self.altitude = 100.0
        self.battery = 100.0
        self.status = "Active"
        self.anomaly_mode = False
        self.anomaly_countdown = random.randint(15, 30) # Time until potential anomaly

    def simulate_movement(self):
        # Check if it's time to trigger an anomaly
        self.anomaly_countdown -= 1
        if self.anomaly_countdown <= 0 and not self.anomaly_mode:
            # 50% chance to trigger an anomaly
            if random.random() < 0.5:
                self.anomaly_mode = True
                print(f"!!! Anomaly Mode Activated for Drone {self.id} !!!")

        if self.anomaly_mode:
            # Simulate anomalous behavior
            # Example 1: Drastic, physically impossible jump
            self.lat += random.uniform(-0.5, 0.5)
            self.lon += random.uniform(-0.5, 0.5)
            # Example 2: Sudden battery failure
            self.battery -= 5.0
        else:
            # Normal behavior
            self.lat += random.uniform(-0.0001, 0.0001)
            self.lon += random.uniform(-0.0001, 0.0001)
            self.altitude += random.uniform(-1, 1)
            self.battery -= 0.05

        if self.battery < 0:
            self.battery = 0
            self.status = "Offline"

    def get_telemetry(self) -> dict:
        self.simulate_movement()
        return {
            "drone_id": str(self.id),
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "lat": self.lat,
                "lon": self.lon,
                "altitude": self.altitude,
            },
            "battery_level": self.battery,
            "status": self.status
        }

async def run_simulator():
    drone_id = uuid.uuid4()
    drone = Drone(drone_id)
    print(f"🛰️ Drone Simulator started for Drone ID: {drone_id}")
    
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        print(f"📡 Connected to backend at {WEBSOCKET_URI}")
        while drone.status != "Offline":
            telemetry_data = drone.get_telemetry()
            await websocket.send(json.dumps(telemetry_data))
            await asyncio.sleep(2)
        print(f"Drone {drone_id} is offline. Simulator shutting down.")

if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except Exception as e:
        print(f"Simulator error: {e}")