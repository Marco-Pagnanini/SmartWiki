FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Prima le dipendenze, così Docker riusa la cache se cambia solo il codice
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codice, configurazione e migrazioni Alembic (.dockerignore esclude cache e .env)
COPY . .

EXPOSE 8000

# Applica le migrazioni mancanti, poi avvia il server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
