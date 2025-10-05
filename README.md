![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Issues](https://img.shields.io/github/issues/moses-varghese/aegis-swarm)
![Pull Requests](https://img.shields.io/github/issues-pr/moses-varghese/aegis-swarm)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/moses-varghese/aegis-swarm)
![GitHub last commit](https://img.shields.io/github/last-commit/moses-varghese/aegis-swarm)

# Aegis Swarm: AI-Powered Secure Drone Swarm Control
Aegis Swarm is a centralized, fully functional, containerized command and control (C2) platform for managing drone swarms. It features a real-time AI anomaly detection engine built with PyTorch to identify and flag cyber-attacks, GPS spoofing, or component failures before they escalate.

Features
Real-Time Swarm Visualization: A dynamic web dashboard with a live map to track the location of all drones.

AI-Powered Anomaly Detection: An unsupervised Autoencoder model detects deviations from normal flight patterns in real-time.

Instant Visual Alerts: Drones under anomalous conditions are immediately flagged in the UI.

Scalable Architecture: Built with FastAPI, React, and containerized with Docker for easy scaling.

Automated Development Workflow: Launch the entire application stack (backend, frontend, simulators) with a single docker-compose command.

Production-Ready Deployment: Includes Kubernetes manifests for deploying to a production environment.

Architecture Overview
The application is built on a microservices-oriented architecture:

Frontend: A React application that provides the user interface, connects to the backend via WebSockets, and visualizes drone data.

Backend: A high-performance FastAPI server that manages WebSocket connections, processes drone data, and uses the AI model to perform anomaly detection.

AI Model: A PyTorch-based Autoencoder trained to recognize normal drone telemetry. It is loaded by the backend at startup.

Simulators: Python scripts that act as virtual drones, sending continuous telemetry data to the backend.

Containerization: The entire application is containerized using Docker and managed with Docker Compose for development and Kubernetes for production.

Technology Stack
Backend: Python, FastAPI, PyTorch, Scikit-learn

Frontend: React, Leaflet.js, Recharts

Dev Environment: Docker, Docker Compose

Deployment: Kubernetes, Nginx

Getting Started
Prerequisites
Ensure you have the following tools installed on your system:

Docker: Get Docker

Docker Compose: (Included with Docker Desktop)

For the production deployment workflow, you will also need:

Minikube: Install Minikube

kubectl: Install kubectl

Development Workflow (Recommended)
This is the easiest way to get the entire application running on your local machine with a single command.

Step 1: Clone the Repository
Bash

git clone <your-repository-url>
cd aegis-swarm
Step 2: Create the Environment File
Navigate into the backend directory and create the .env file by copying the example.

Bash

cd backend
cp .env.example .env
cd .. 
Step 3: Run the Application
From the root of the project directory, run the following command:

Bash

docker-compose up --build
This command will:

Build the Docker images for all services.

Start a container to train the AI model and save the files to a shared volume.

Start the backend container, which waits for the training to complete before loading the models.

Start the frontend container.

Start the drone swarm simulator, which connects to the backend.

Step 4: View the Application
Open your web browser and navigate to http://localhost:3000. You should see the map and drones appearing within a few seconds.

Step 5: Stop the Application
To stop all running services, press Ctrl+C in the terminal, and then run:

Bash

docker-compose down
Production Deployment Workflow (Kubernetes)
This workflow deploys the application to a local Kubernetes cluster using Minikube.

Step 1: Start Minikube
Bash

minikube start
Step 2: Point Docker to Minikube's Environment
In the same terminal, run this command to ensure the images you build are visible to Minikube:

Bash

eval $(minikube -p minikube docker-env)
Step 3: Build Production Docker Images
From the project root, build the production-ready images:

Bash

docker build -t aegis-swarm-backend ./backend
docker build -t aegis-swarm-frontend ./frontend
(Note: For this to work, ensure your frontend/Dockerfile is the multi-stage production version with Nginx, not the development version.)

Step 4: Deploy to Kubernetes
Apply all the Kubernetes manifest files with a single command:

Bash

kubectl apply -f kubernetes/
This will create the training job, deployments, and services in your cluster.

Step 5: Access the Application
Find the URL for the frontend service:

Bash

minikube service frontend-service
This command will automatically open the application URL in your browser.

Step 6: Run Simulators Manually
To provide data to your Kubernetes deployment, run the simulator script locally:

Bash

# Make sure to activate the Python virtual environment first
python swarm_launcher.py
(Note: Configure the simulator's WebSocket URI to point to the external IP of your Kubernetes service.)

Project Structure
aegis-swarm/
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   │   ├── model.py
│   │   │   ├── train.py
│   │   │   └── anomaly_detector.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── healthcheck.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   └── App.js
│   ├── Dockerfile
│   └── Dockerfile.dev
├── kubernetes/
│   ├── 01-pvc.yaml
│   ├── 02-training-job.yaml
│   ├── ...
│   └── 06-frontend-service.yaml
├── simulators/
│   └── drone_simulator.py
├── docker-compose.yml
├── swarm_launcher.py
└── README.md
