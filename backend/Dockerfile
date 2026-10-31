FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, so Docker reuses the cache when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codice, configurazione e migrazioni Alembic (.dockerignore esclude cache e .env)
COPY . .

EXPOSE 8000

# Apply pending migrations, then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
