import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="../.env")

# Initialize the FastAPI app
app = FastAPI(title=os.getenv("PROJECT_NAME", "Aegis Swarm"))

# Get CORS origins from environment variables
# The split(',') creates a list from a comma-separated string
origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")

# Add CORS middleware to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """
    Root endpoint to check if the server is running.
    """
    return {"message": f"Welcome to {app.title}"}


@app.websocket("/ws/drone")
async def websocket_endpoint(websocket: WebSocket):
    """
    Placeholder WebSocket endpoint for drone communication.
    We will build this out in the next steps.
    """
    await websocket.accept()
    print("Drone WebSocket connection established.")
    try:
        while True:
            # For now, just keep the connection open
            # Later, this will receive telemetry and send commands
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Drone WebSocket connection closed.")