FROM node:22-alpine AS frontend-build

WORKDIR /web

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build


FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    MEMORY_PATH=/data/memory.json \
    CARD_STORE_PATH=/data/cards.json

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY --from=frontend-build /web/out ./frontend/out

# Persistent per-user memory lives here (Maritime keeps the micro-VM disk).
RUN mkdir -p /data

EXPOSE 8080

# The Python launcher reads Maritime's injected PORT without shell expansion.
CMD ["python", "-m", "app.start"]
