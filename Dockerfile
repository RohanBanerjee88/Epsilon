FROM node:22-alpine AS frontend-build

WORKDIR /web

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
ARG NEXT_PUBLIC_BASE_PATH=/a/dfe76a89-ace9-4be1-9dff-924ffe9223b5
ENV NEXT_PUBLIC_BASE_PATH=$NEXT_PUBLIC_BASE_PATH
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
CMD ["/usr/local/bin/python", "-m", "app.start"]
