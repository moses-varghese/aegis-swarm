import os
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.ml.anomaly_detector import AnomalyDetector

# --- Connection Manager for Frontend Clients ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


# --- App Initialization ---
load_dotenv(dotenv_path="../.env")

try:
    detector = AnomalyDetector()
except FileNotFoundError:
    print("MODEL/SCALER NOT FOUND. Please run the training script: python app/ml/train.py")
    detector = None

app = FastAPI(title=os.getenv("PROJECT_NAME", "Aegis Swarm"))

origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Endpoints ---
@app.get("/")
async def read_root():
    return {"message": f"Welcome to {app.title}"}


@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """WebSocket for the frontend dashboard to connect to."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard connection closed.")


@app.websocket("/ws/drone")
async def websocket_drone_endpoint(websocket: WebSocket):
    """WebSocket for drone simulators to connect and send data."""
    await websocket.accept()
    print("Drone WebSocket connection established.")
    if not detector:
        await manager.broadcast("Error: Anomaly detector not initialized.")
        return

    try:
        while True:
            data = await websocket.receive_text()
            telemetry = json.loads(data)
            
            # Perform anomaly detection
            result = detector.predict(telemetry)
            
            # Combine telemetry with the analysis result
            output_data = {**telemetry, **result}
            
            # Broadcast the combined data to all connected dashboards
            await manager.broadcast(json.dumps(output_data))
            
    except WebSocketDisconnect:
        print("Drone WebSocket connection closed.")
    except Exception as e:
        print(f"An error occurred in the Drone WebSocket: {e}")