# ================================
# 1. Base Builder Stage
# ================================
FROM python:3.13-alpine AS builder

# Install build dependencies required by some Python packages, including C++, Rust, and C compilers
# g++ provides the C++ compiler
RUN apk add --no-cache gcc g++ musl-dev libffi-dev rust cargo

# Set the working directory
WORKDIR /app

# Install uv globally
RUN pip install uv

# Copy the requirements file first to leverage Docker's cache
COPY requirements.txt .

# Install dependencies into the system environment using uv
RUN uv pip install --system -r requirements.txt


# ================================
# 2. Runtime Stage
# ================================
FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy the installed Python packages from the builder stage
# This is where uv installed them with the --system flag
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy the rest of your application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]