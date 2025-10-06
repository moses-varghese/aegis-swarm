# import os
# import json
# from typing import List
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from app.ml.anomaly_detector import AnomalyDetector

# # --- Connection Manager for Frontend Clients ---
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()

# # --- App Initialization ---
# load_dotenv(dotenv_path="../.env")

# detector = AnomalyDetector()

# app = FastAPI(title=os.getenv("PROJECT_NAME", "Aegis Swarm"))

# origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- API Endpoints ---
# @app.get("/")
# async def read_root():
#     return {"message": f"Welcome to {app.title}"}

# @app.websocket("/ws/dashboard")
# async def websocket_dashboard_endpoint(websocket: WebSocket):
#     """WebSocket for the frontend dashboard to connect to."""
#     await manager.connect(websocket)
#     try:
#         while True:
#             await websocket.receive_text() # Keep connection alive
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         print("Dashboard connection closed.")

# @app.websocket("/ws/drone")
# async def websocket_drone_endpoint(websocket: WebSocket):
#     """WebSocket for drone simulators to connect and send data."""
#     await websocket.accept()
#     print("Drone WebSocket connection established.")

#     try:
#         while True:
#             data = await websocket.receive_text()
#             telemetry = json.loads(data)

#             # Perform anomaly detection
#             result = detector.predict(telemetry)

#             # Combine telemetry with the analysis result
#             output_data = {**telemetry, **result}

#             # Broadcast the combined data to all connected dashboards
#             await manager.broadcast(json.dumps(output_data))

#     except WebSocketDisconnect:
#         print("Drone WebSocket connection closed.")
#     except Exception as e:
#         print(f"An error occurred in the Drone WebSocket: {e}")




import os
import json
import asyncio
import redis # Import redis
from typing import List, Dict
from datetime import datetime # Import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.ml.anomaly_detector import AnomalyDetector


# --- Redis Connection ---
try:
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("Backend connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    redis_client = None

# --- Connection Managers ---
class ConnectionManager:
    def __init__(self):
        # Dictionary to store active drone connections, keyed by drone_id
        self.active_drone_connections: Dict[str, WebSocket] = {}
        # List for frontend dashboard connections
        self.active_dashboard_connections: List[WebSocket] = []

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.active_dashboard_connections.append(websocket)

    def disconnect_dashboard(self, websocket: WebSocket):
        self.active_dashboard_connections.remove(websocket)
        
    async def connect_drone(self, websocket: WebSocket, drone_id: str):
        await websocket.accept()
        self.active_drone_connections[drone_id] = websocket

    def disconnect_drone(self, drone_id: str):
        if drone_id in self.active_drone_connections:
            del self.active_drone_connections[drone_id]
            
    async def broadcast_to_dashboards(self, message: str):
        for connection in self.active_dashboard_connections:
            await connection.send_text(message)

    async def send_command_to_drone(self, drone_id: str, command: dict):
        if drone_id in self.active_drone_connections:
            websocket = self.active_drone_connections[drone_id]
            await websocket.send_text(json.dumps(command))
            return True
        return False

manager = ConnectionManager()

# --- App Initialization ---
load_dotenv(dotenv_path="../.env")
detector = AnomalyDetector()
app = FastAPI(title=os.getenv("PROJECT_NAME", "Aegis Swarm"))
# origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The backend will now also listen to Redis to confirm alerts
# def alert_listener(manager_instance):
#     # ... (same redis connection logic as alerting_service.py)
#     pubsub = r.pubsub(ignore_subscribe_messages=True)
#     pubsub.subscribe('alerts')
#     print("Backend is listening for its own alerts to confirm.")
#     for message in pubsub.listen():
#         # This is just for logging/confirmation in the backend
#         print(f"CONFIRMED ALERT PUBLISHED: {message['data']}")

# --- API Endpoints ---
@app.post("/api/drones/{drone_id}/command")
async def send_command(drone_id: str, command: dict):
    """
    API endpoint to send a command to a specific drone.
    Example body: {"command": "RTB"}
    """
    success = await manager.send_command_to_drone(drone_id, command)
    if not success:
        raise HTTPException(status_code=404, detail="Drone not found or not connected")
    return {"message": f"Command '{command.get('command')}' sent to drone {drone_id}"}

# @app.on_event("startup")
# async def startup_event():
#     # Start a background thread to listen to redis for confirmation
#     threading.Thread(target=alert_listener, args=(manager,), daemon=True).start()

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {app.title}"}

@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    await manager.connect_dashboard(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)
        print("Dashboard connection closed.")

@app.websocket("/ws/drone/{drone_id}")
async def websocket_drone_endpoint(websocket: WebSocket, drone_id: str):
    await manager.connect_drone(websocket, drone_id)
    print(f"Drone {drone_id} connected.")
    try:
        while True:
            # Drones now listen for both telemetry and commands
            data = await websocket.receive_text()
            telemetry = json.loads(data)
            
            result = detector.predict(telemetry)
            output_data = {**telemetry, **result}


            # Add a 'type' to the telemetry data
            output_data['type'] = 'telemetry'
            await manager.broadcast_to_dashboards(json.dumps(output_data))

            # NEW: Publish to Redis if a classified anomaly is found
            if result["is_anomaly"] and result["anomaly_type"] not in ["Normal", "None"]:
                alert_message = {
                    "type": "alert",
                    "timestamp": datetime.utcnow().isoformat(),
                    "drone_id": drone_id,
                    "anomaly_type": result['anomaly_type']
                }
                # Publish to Redis for external systems
                if redis_client:
                    redis_client.publish('alerts', json.dumps(alert_message))
                # AND broadcast directly to dashboards
                await manager.broadcast_to_dashboards(json.dumps(alert_message))
            
    except WebSocketDisconnect:
        manager.disconnect_drone(drone_id)
        print(f"Drone {drone_id} disconnected.")
    except Exception as e:
        print(f"An error occurred for drone {drone_id}: {e}")