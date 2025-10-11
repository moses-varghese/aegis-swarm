# import asyncio
# import websockets
# import json
# import random
# import uuid
# from datetime import datetime

# # WEBSOCKET_URI = "ws://localhost:8000/ws/drone"
# WEBSOCKET_URI = "ws://backend:8000/ws/drone"

# class Drone:
#     def __init__(self, drone_id):
#         self.id = drone_id
#         self.lat = 8.5241 + random.uniform(-0.05, 0.05)
#         self.lon = 76.9366 + random.uniform(-0.05, 0.05)
#         self.altitude = 100.0
#         self.battery = 100.0
#         self.status = "Active"
#         self.anomaly_mode = False
#         self.anomaly_countdown = random.randint(15, 30) # Time until potential anomaly

#     def simulate_movement(self):
#         # Check if it's time to trigger an anomaly
#         self.anomaly_countdown -= 1
#         if self.anomaly_countdown <= 0 and not self.anomaly_mode:
#             # 50% chance to trigger an anomaly
#             if random.random() < 0.5:
#                 self.anomaly_mode = True
#                 print(f"!!! Anomaly Mode Activated for Drone {self.id} !!!")

#         if self.anomaly_mode:
#             # Simulate anomalous behavior
#             # Example 1: Drastic, physically impossible jump
#             self.lat += random.uniform(-0.5, 0.5)
#             self.lon += random.uniform(-0.5, 0.5)
#             # Example 2: Sudden battery failure
#             self.battery -= 5.0
#         else:
#             # Normal behavior
#             self.lat += random.uniform(-0.0001, 0.0001)
#             self.lon += random.uniform(-0.0001, 0.0001)
#             self.altitude += random.uniform(-1, 1)
#             self.battery -= 0.05

#         if self.battery < 0:
#             self.battery = 0
#             self.status = "Offline"

#     def get_telemetry(self) -> dict:
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
#     drone_id = uuid.uuid4()
#     drone = Drone(drone_id)
#     print(f"🛰️ Drone Simulator started for Drone ID: {drone_id}")
    
#     async with websockets.connect(WEBSOCKET_URI) as websocket:
#         print(f"📡 Connected to backend at {WEBSOCKET_URI}")
#         while drone.status != "Offline":
#             telemetry_data = drone.get_telemetry()
#             await websocket.send(json.dumps(telemetry_data))
#             await asyncio.sleep(2)
#         print(f"Drone {drone_id} is offline. Simulator shutting down.")

# if __name__ == "__main__":
#     try:
#         asyncio.run(run_simulator())
#     except Exception as e:
#         print(f"Simulator error: {e}")




import asyncio
import websockets
import json
import random
import uuid
from datetime import datetime
from pythonjsonlogger import jsonlogger
import logging
import sys

# --- Structured Logging Configuration ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonjsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
# Avoid adding duplicate handlers if this script is imported
if not logger.handlers:
    logger.addHandler(logHandler)

# The base URI for WebSocket connections
WEBSOCKET_URI_BASE = "ws://backend:8000/ws/drone/"

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
                logger.warning("Anomaly Mode Activated.", extra={'drone_id': self.id})

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

    async def handle_commands(self, websocket):
        """Listen for commands from the backend."""
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
            command_data = json.loads(message)
            if command_data.get("command") == "RTB":
                logger.info("Received RTB command.", extra={'drone_id': self.id})
                self.status = "Returning to Base"
        except asyncio.TimeoutError:
            pass # No command received, continue normally
        except Exception:
            logger.error("Error processing command.", extra={'drone_id': self.id}, exc_info=True)

async def run_simulator(drone_id):
    drone = Drone(drone_id)
    uri = WEBSOCKET_URI_BASE + str(drone_id)
    logger.info(f"Simulator starting.", extra={'drone_id': drone_id, 'uri': uri})
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Successfully connected to backend.", extra={'drone_id': drone_id})
            while drone.status not in ["Offline", "Landed"]:
                # Listen for commands in a non-blocking way
                await drone.handle_commands(websocket)

                # Send telemetry
                telemetry_data = drone.get_telemetry()
                await websocket.send(json.dumps(telemetry_data))
                logger.debug("Telemetry sent.", extra={'drone_id': drone_id})
                
                await asyncio.sleep(2)
            logger.info("Drone is offline. Simulator shutting down.", extra={'drone_id': drone_id})
    except websockets.exceptions.ConnectionClosedError as e:
        logger.error(f"Connection to backend lost: {e}", extra={'drone_id': drone_id})
    except Exception:
        logger.error("An unexpected error occurred in the simulator.", extra={'drone_id': drone_id}, exc_info=True)

# Update the main execution block to pass a unique ID
if __name__ == "__main__":
    # drone_id = uuid.uuid4()
    if len(sys.argv) > 1:
        drone_id = sys.argv[1]
    else:
        drone_id = str(uuid.uuid4())
    try:
        asyncio.run(run_simulator(drone_id))
    except Exception as e:
        logger.error(extra={'Simulator error': e})