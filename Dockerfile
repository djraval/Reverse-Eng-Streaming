FROM python:3.11-slim

WORKDIR /app

# Add build argument and environment variable for PORT
ARG PORT
ENV PORT=${PORT}

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Create a virtual environment
RUN uv venv /app/venv

# Activate the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN uv pip install -r requirements.txt

# Copy only the necessary application code
COPY main.py .
COPY channels.json .

# Create directory for logs
RUN mkdir -p /app/logs && \
    touch /app/logs/app.log && \
    chmod 777 /app/logs/app.log

# Expose the configurable port
EXPOSE ${PORT}

# Command to run the application
CMD ["python", "main.py"]
