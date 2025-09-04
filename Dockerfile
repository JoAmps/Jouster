# ================================
# 1. Base Builder Stage
# ================================
FROM python:3.13-alpine AS builder

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies into system environment
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# 2. Runtime Stage
# ================================
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]