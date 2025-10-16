FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application code
COPY backend/app /app/app

# Copier les fichiers statiques du frontend pour servir l'UI depuis le backend
COPY frontend/public /app/static

# Render supplies PORT; default to 8000 for local
ENV PORT=8000
EXPOSE 8000

# Start FastAPI on the provided port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]