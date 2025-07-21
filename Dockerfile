FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user to run the app
RUN adduser --disabled-password --gecos "" appuser

# Create tiktoken cache directory and set permissions
RUN mkdir -p /usr/local/lib/python3.10/site-packages/llama_index/core/_static/tiktoken_cache/ && \
    chmod 777 /usr/local/lib/python3.10/site-packages/llama_index/core/_static/tiktoken_cache/

# Set ownership for app directory
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]