import subprocess
import sys
import time

# --- A Python Script to Launch a Swarm of Drones ---

NUM_DRONES = 5

print(f"🚀 Launching a swarm of {NUM_DRONES} drones...")

processes = []

# Determine the correct python executable from the virtual environment
python_executable = "python"

# Launch all the drone simulator processes
for i in range(NUM_DRONES):
    print(f"Launching drone #{i+1}...")
    # Popen runs the command in a new process
    proc = subprocess.Popen([python_executable, "simulators/drone_simulator.py"])
    processes.append(proc)
    time.sleep(0.5) # Stagger the launches slightly

print(f"✅ Swarm of {len(processes)} drones launched.")
print("Press Ctrl+C in this terminal to stop all simulators.")

try:
    # Wait for user to press Ctrl+C
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Terminating all drone simulators...")
    for proc in processes:
        proc.terminate() # This sends a signal to stop the process
    print("All simulators stopped.")