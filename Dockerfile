# Dockerfile for Railway - InstaCollect with Playwright
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port (Railway will override this with $PORT)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
