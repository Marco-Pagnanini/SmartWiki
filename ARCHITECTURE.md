# ARCHITECTURE

Specifiche dell'architettura di **Smart Wiki**: wiki aziendale di documenti con chatbot AI. Il documento descrive lo stato attuale (monolite modulare) e la proposta a microservizi (vedi panel "Architettura 2").

## 1. Panoramica

- Template: PostgreSQL (pgvector) + backend FastAPI + frontend React, avviabili con `docker compose up --build`.
- L'utente dialoga con una chat; un **orchestrator** AI delega a due **sub agenti** (researcher, archivist) che operano sulla wiki tramite tool esposti da un **server MCP**.
- Un documento ha: `id` (UUID), `name_of_file` (univoco), `group_number` (intero >= 1), `summary` (opzionale).

## 2. Stack

| Livello | Tecnologia |
|---|---|
| Frontend | React 19, TypeScript 7, Vite 8; build servita da nginx:alpine |
| Backend | Python 3.12, FastAPI 0.162, uvicorn, Pydantic Settings 2.16 |
| Persistenza | SQLAlchemy 2.1, psycopg 3.3, Alembic 1.20 |
| Database | PostgreSQL 17 con estensione pgvector (immagine `pgvector/pgvector:pg17`) |
| AI | SDK `anthropic` 2.3, modello `claude-haiku-5-5`, effort `low` |
| Tool AI | `mcp` 2.3 (server e client, streamable HTTP stateless) |
| Infra | Docker Compose (db, backend, frontend) |

## 3. Struttura del repository

```
SmartWiki/
  docker-compose.yml, .env.example, README.md
  backend/
    Dockerfile, requirements.txt, alembic.ini
    alembic/                  migrazioni (env.py importa le entity)
    app/
      main.py                 FastAPI, CORS, router, mount MCP su "/"
      mcp_server.py           istanza MCPServer
      api/                    chat.py, health.py, doc.py (bozza, non registrato)
      core/                   config.py (Settings), doc.py (entity Doc)
      db/session.py           engine, SessionLocal, Base, get_db
      service/doc.py          create_doc, get_doc, get_doc_by_name
      tools/doc.py            tool MCP add_document, get_document_by_name
      agents/                 orchestrator, researcher, wiki (archivist),
                              runner, mcp_client
  frontend/
    Dockerfile, nginx.conf, vite.config.ts
    src/                      main.tsx, App.tsx, App.css
```

## 4. Flusso di una richiesta chat

1. L'utente scrive nella chat (`App.tsx`), che invia `POST /api/chat` con `message` e `history`.
2. Nginx (porta 3000) fa da reverse proxy di `/api/` verso `backend:8000` (timeout 180 s).
3. `api/chat.py` valida la richiesta e chiama `orchestrator.run(message, history)`.
4. L'orchestrator esegue `run_agent` con due local tool: `ask_researcher` e `ask_archivist`.
5. Il sub agente scelto esegue a sua volta `run_agent` con un solo tool MCP consentito.
6. `run_agent` cicla (max 10 turni): chiama Claude, esegue i `tool_use` (locali o via client MCP), rimanda i `tool_result`, finche' il modello non risponde in testo.
7. I tool MCP (`/mcp`) usano il service documenti e quindi PostgreSQL.
8. La risposta risale fino al frontend come `{ "reply": "..." }`.

## 5. Componenti backend

### 5.1 API HTTP
| Endpoint | Descrizione |
|---|---|
| `GET /api/health` | stato del backend, restituisce `{status, app}` |
| `GET /api/health/db` | `SELECT 1`; 503 se il database non risponde |
| `POST /api/chat` | `ChatRequest {message (1-4000), history (max 50 di {role, content})}` -> `{reply}`; 503 senza `ANTHROPIC_API_KEY`, 502 su errore API Claude |
| `/api/doc` | bozza incompleta in `api/doc.py`, non registrata in `main.py` |
| `/mcp` | server MCP (streamable HTTP, stateless), montato su "/" per ultimo cosi' da non essere rediretto |

### 5.2 Agenti
- **Orchestrator** (`orchestrator.py`): parla con l'utente, decide a chi delegare, non legge ne' modifica la wiki direttamente. Ogni task ai sub agenti deve essere completo e autosufficiente (non vedono la conversazione). Chiede all'utente i dati mancanti invece di inventarli.
- **Researcher** (`researcher.py`): sola lettura, tool `get_document_by_name` (solo nome file esatto; no ricerca per tema, gruppo o nome parziale).
- **Archivist** (`wiki.py`): sola creazione, tool `add_document`; non ritenta con nomi diversi se il nome esiste.
- **Runner** (`runner.py`): loop agentico, `MAX_TURNS = 10`, `max_tokens = 2000`; gli errori dei sub agenti diventano `tool_result` con `is_error`.
- **MCP client** (`mcp_client.py`): `connect()`, `get_tools(allowed)` (converte i tool MCP nel formato API Claude e segnala nomi non esistenti), `call_tool()`.

### 5.3 Tool MCP (`tools/doc.py`)
| Tool | Input | Esito |
|---|---|---|
| `add_document` | `name_of_file` (1-255), `group_number` (>= 1), `summary` (<= 2000, opz.) | documento creato; `ToolError` se il nome esiste |
| `get_document_by_name` | `name_of_file` esatto | documento; `ToolError` se assente |

### 5.4 Dati
Tabella `documents` (entity `Doc`, `core/doc.py`):

| Colonna | Tipo | Vincoli |
|---|---|---|
| `id` | UUID | PK, default `uuid4` |
| `name_of_file` | String(255) | unique (`uq_documents_name_of_file`) |
| `group_number` | Integer | indice `ix_documents_group_number` |
| `summary` | String(2000) | nullable |

`db/session.py` usa `pool_pre_ping`, `SessionLocal`, `get_db` e una naming convention per indici e vincoli (necessaria per downgrade Alembic).

Migrazioni: `27ff64b1a017` (crea `documents`), `14dbc9c2d676` (nome file univoco). Applicate a ogni avvio con `alembic upgrade head`.

## 6. Frontend
- Interfaccia chatbot ispirata a Gemini, con logo e colori dello struzzo.
- Stato locale: `messages`, `input`, `loading`; mini renderer Markdown; invio con Invio.
- In Docker: nginx serve la build e fa proxy di `/api/`. In sviluppo (`npm run dev`, porta 5173) il proxy e' quello di Vite verso `localhost:8000`.

## 7. Configurazione (`.env`)
| Variabile | Uso |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | credenziali del database |
| `DATABASE_URL` | connessione SQLAlchemy (`postgresql+psycopg://...@db:5432/...`) |
| `APP_NAME` | nome app (titolo FastAPI e server MCP) |
| `CORS_ORIGINS` | origini ammesse (serve solo con `npm run dev`) |
| `ANTHROPIC_API_KEY` | chiave API Claude |
| `ANTHROPIC_MODEL` | default `claude-haiku-5-5` |
| `ANTHROPIC_EFFORT` | `low` / `medium` / `high` / `xhigh` / `max`, default `low` |
| `MCP_URL` | default `http://localhost:8000/mcp` |

## 8. Deploy locale (Docker Compose)
- `db`: pgvector pg17, porta 5432, volume `postgres_data`, healthcheck `pg_isready`.
- `backend`: build `./backend`, cartella montata come volume, `alembic upgrade head` poi uvicorn `--reload`, porta 8000, parte quando `db` e' healthy.
- `frontend`: build multi-stage (node:22 -> nginx), porta 3000.
- Avvio: `cp .env.example .env && docker compose up --build`.

## 9. Note e limiti attuali
- `api/doc.py` e' incompleto e non registrato.
- pgvector e' disponibile ma non ancora usato.
- Nessuna ricerca per tema/gruppo, nessun update o delete di documenti.
- Il client MCP degli agenti si collega al backend stesso (`MCP_URL`): in Docker va impostato un host raggiungibile dal container.
- Nessuna autenticazione sulle API.

## 10. Architettura a microservizi (proposta, panel "Architettura 2")

Separazione per responsabilita', un servizio per ogni agente e uno per il dominio documenti.

| Servizio | Responsabilita' | Espone | Dipende da |
|---|---|---|---|
| `web` | frontend React + nginx | HTTP :3000 | `gateway` |
| `gateway` | entry point `/api/*`, validazione chat, health aggregato | `POST /api/chat`, `GET /api/health` | `orchestrator-service` |
| `orchestrator-service` | conversazione e delega ai sub agenti | `POST /run` | `research-service`, `archivist-service`, API Claude |
| `research-service` | agente researcher (sola lettura) | `POST /run` | `doc-service` (MCP), API Claude |
| `archivist-service` | agente archivist (sola creazione) | `POST /run` | `doc-service` (MCP), API Claude |
| `doc-service` | dominio documenti: unico proprietario di DB e migrazioni | MCP `/mcp` (+ REST `/docs`) | `postgres` |
| `postgres` | database `documents` (pgvector) | SQL :5432 | solo `doc-service` |

Principi:
- **Database per servizio**: solo `doc-service` accede a PostgreSQL e gestisce Alembic; gli altri passano dai tool MCP.
- **Libreria condivisa `agent-runtime`**: runner, client MCP e configurazione Claude, usata dai tre servizi agente (pacchetto Python, non un servizio).
- **Comunicazione sincrona** HTTP/JSON tra orchestrator e sub agenti; MCP tra agenti e `doc-service`.
- **Privilegi minimi**: researcher ottiene solo `get_document_by_name`, archivist solo `add_document`.
- **Evoluzioni naturali**: un `search-service` con pgvector per la ricerca semantica, auth nel gateway, code per task lunghi.
