FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY stream_extractor.py .
RUN mkdir -p logs
CMD ["python", "stream_extractor.py"]