# GLASSEYE AI OS - Production Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    git \
    curl \
    wget \
    netcat-traditional \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all GLASSEYE Python modules
COPY *.py ./

# Create necessary directories
RUN mkdir -p /app/memory /app/logs /app/results

# Copy memory directory
COPY memory /app/memory

# Expose ports
EXPOSE 8002 5002 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/ || exit 1

# Default command - run GLASSEYE AI server
CMD ["python3", "glasseye_ai_server.py"]
