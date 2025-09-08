# ================================
# 1. Base Builder Stage
# ================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build tools & dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (leverage Docker cache)
COPY requirements.txt .

# Upgrade pip to ensure latest wheels are used
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt punkt_tab wordnet stopwords \
    averaged_perceptron_tagger averaged_perceptron_tagger_eng \
    && mkdir -p /usr/local/nltk_data \
    && cp -r /root/nltk_data/* /usr/local/nltk_data/

# ================================
# 2. Runtime Stage
# ================================
FROM python:3.13-slim

WORKDIR /app

# Ensure NLTK data is available in runtime image
COPY --from=builder /usr/local/nltk_data /usr/local/nltk_data
ENV NLTK_DATA=/usr/local/nltk_data

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]