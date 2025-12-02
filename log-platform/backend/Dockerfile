FROM python:3.11-slim-bookworm

# Disable caching to avoid stale indexes
ENV PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies only (no system packages required)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app /app/app

# Expose API port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

