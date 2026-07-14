FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    MEMORY_PATH=/data/memory.json

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Persistent per-user memory lives here (Maritime keeps the micro-VM disk).
RUN mkdir -p /data

EXPOSE 8080

# Honor $PORT if the platform injects one; default to 8080.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
