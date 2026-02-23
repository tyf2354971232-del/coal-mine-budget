# ── Stage 1: Build Vue frontend ──
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npx vite build

# ── Stage 2: Python backend + static files ──
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install bcrypt==4.2.1

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist ./static

# Copy data txt files used by seed scripts
COPY *.txt ./data/

ENV PORT=8001
ENV DATA_DIR=/app/data
EXPOSE ${PORT}

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
