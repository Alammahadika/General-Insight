# Dockerfile for Fly.io - Demo Mode (No Playwright)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Fly.io will set PORT env var)
EXPOSE 8080

# Run the application
CMD uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080}
