import subprocess
import sys
import time
import uuid
import logging
from pythonjsonlogger import jsonlogger

# --- A Python Script to Launch a Swarm of Drones ---

# --- Structured Logging Configuration ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

NUM_DRONES = 5

logger.info(f"Launching a swarm of {NUM_DRONES} drones...")

processes = []

# Determine the correct python executable from the virtual environment
python_executable = "python"

# Launch all the drone simulator processes
for i in range(NUM_DRONES):
    drone_id = uuid.uuid4()
    logger.info(f"Launching drone process #{i+1}", extra={'drone_id': drone_id})
    # Popen runs the command in a new process
    try:
        proc = subprocess.Popen([python_executable, "simulators/drone_simulator.py", str(drone_id)])
        processes.append(proc)
        time.sleep(0.5) # Stagger the launches slightly
    except Exception:
        logger.critical("Failed to launch a drone simulator process.", exc_info=True)

logger.info(f"Swarm of {len(processes)} drones launched successfully.")
logger.info("Press Ctrl+C in this terminal to stop all simulators.")

try:
    # Wait for user to press Ctrl+C
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.warning("Termination signal received. Stopping all drone simulators...")
    for proc in processes:
        proc.terminate() # This sends a signal to stop the process
    logger.info("All simulators stopped.")