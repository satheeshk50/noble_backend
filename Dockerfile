# Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports (FastAPI: 8000, FastMCP: 8001 or anything else)
EXPOSE 8000
EXPOSE 3001

# This Dockerfile will be used by both containers, so no CMD here
