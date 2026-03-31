# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy entire project
COPY . .

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:10000/health').read()" || exit 1

# Start application
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 --worker-class sync --timeout 120 --access-logfile - --error-logfile - server:app"]
