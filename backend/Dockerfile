FROM python:3.11-slim

# Install Stockfish from Debian's package manager
# This works because we control the OS in Docker
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Start the server
CMD uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
