# Smart Wiki

Template di partenza per il progetto Smart Wiki: database **PostgreSQL** (con pgvector), backend **FastAPI** e frontend **React**, avviabili con un solo comando.

## Prerequisiti

- [Docker](https://docs.docker.com/get-docker/) con Docker Compose (incluso in Docker Desktop)

## Avvio

```bash
cp .env.example .env
docker compose up --build
```

Prima di usare il progetto fuori dal tuo computer, cambia la password in `.env`.

## Indirizzi utili

| Cosa | Indirizzo |
|---|---|
| Frontend | http://localhost:3000 |
| Documentazione API (Swagger) | http://localhost:8000/docs |
| Health check database | http://localhost:8000/api/health/db |

Il database è raggiungibile anche da un client SQL su `localhost:5432`, con le credenziali scritte in `.env`.

## Fermare tutto

```bash
docker compose down
```

Per cancellare anche i dati del database (volume `postgres_data`):

```bash
docker compose down -v
```

## Sviluppo

**Backend:** la cartella `backend` è montata nel container e uvicorn gira con `--reload`, quindi ogni modifica viene ricaricata automaticamente, senza ricostruire l'immagine.

**Frontend fuori da Docker:** con i container avviati, in un altro terminale:

```bash
cd frontend && npm install && npm run dev
```

L'app sarà su http://localhost:5173; le chiamate a `/api` vengono inoltrate al backend su `localhost:8000` dal proxy di Vite.

## Migrazioni del database (Alembic)

Le migrazioni mancanti vengono applicate in automatico a ogni avvio del backend.

Dopo aver creato o modificato un'entity, genera la migrazione:

```bash
docker compose exec backend alembic revision --autogenerate -m "descrizione della modifica"
```

Il file viene creato in `backend/alembic/versions/`: controllalo, poi applicalo con:

```bash
docker compose exec backend alembic upgrade head
```

Ogni nuovo file che contiene entity va importato in `backend/alembic/env.py`, altrimenti Alembic non vede le sue tabelle.
