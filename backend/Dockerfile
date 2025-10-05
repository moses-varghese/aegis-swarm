# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the new healthcheck script
COPY healthcheck.py .

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# We point to the main.py inside the app directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]