# E-Commerce AI Agent

An AI assistant for small e-commerce businesses. Customers can ask about orders, refunds, shipping, payments, and products. Answers are grounded in real business data (orders, products) and company policy documents (RAG).

This is a **microservices** learning project: separate Python services, separate databases, HTTP-only communication, and a React frontend behind an API gateway.

## Architecture

```mermaid
flowchart LR
    FE[React Frontend :5173] --> GW[API Gateway :8000]
    GW -->|login / me| AUTH[Auth Service :8001]
    GW -->|chat| AGENT[Agent Service :8004]
    AGENT -->|orders / products| BIZ[Business Service :8003]
    AGENT -->|ask| RAG[RAG Service :8002]
    AUTH --> AUTH_DB[(auth_db)]
    BIZ --> BIZ_DB[(business_db)]
    RAG --> RAG_DB[(rag_db)]
    RAG --> OPENAI[OpenAI API]
```

| Service | Port | Database | Responsibility |
|---------|------|----------|----------------|
| **API Gateway** | 8000 | — | Public entry point, JWT validation, routing |
| **Auth Service** | 8001 | `auth_db` | Login, JWT, users & roles |
| **RAG Service** | 8002 | `rag_db` | PDF ingest, embeddings, policy Q&A |
| **Business Service** | 8003 | `business_db` | Products, orders, customers |
| **Agent Service** | 8004 | — | Intent detection, orchestration |
| **Frontend** | 5173 | — | Login + chat UI |

---

## What is built so far

### Phase 1 — Backend microservices

| Step | What we built | Key libraries |
|------|---------------|---------------|
| **Auth** | Login, JWT, `/me`, bcrypt passwords | FastAPI, SQLAlchemy 2.0, `bcrypt`, `python-jose`, PostgreSQL |
| **Business** | Product search, order lookup, order ownership | FastAPI, SQLAlchemy 2.0, PostgreSQL |
| **RAG** | PDF → chunks → OpenAI embeddings → pgvector retrieval → LLM answer | FastAPI, `pypdf`, `openai`, `pgvector`, `langchain-text-splitters`, PostgreSQL |
| **Agent** | Keyword intent routing → calls Business or RAG | FastAPI, `httpx` |
| **API Gateway** | Proxies `/api/auth/*` and `/api/chat` | FastAPI, `httpx`, CORS |
| **Contracts** | Shared Pydantic models + internal API key helpers | `pydantic`, `fastapi` (in `backend/packages/contracts`) |

**Agent intents:** `order_status`, `refund_policy`, `shipping_policy`, `payment_policy`, `faq`, `product_info`, `general`.

**Security:**
- Chat uses JWT when logged in (gateway validates token, passes trusted `user_id` to agent).
- Internal services require `X-Internal-API-Key` header.
- Order lookup checks that the order belongs to the logged-in customer.

### Phase 2 — Frontend

| What we built | Key libraries |
|---------------|---------------|
| Login, guest mode, chat UI with intent/sources display | React 19, TypeScript, Vite |

### Knowledge base (RAG documents)

Policy PDFs live in `backend/documents/` (refund, shipping, payment, warranty, FAQ). Text sources are in `backend/documents/content/`. Ingest with the knowledge seeder (see below).

---

## Prerequisites

- **Python 3.11+** (project tested with 3.14)
- **Node.js 18+** and npm
- **PostgreSQL 15+** with the **pgvector** extension (for `rag_db`)
- **OpenAI API key** (for RAG embeddings + answers)
- `psql` CLI (or any PostgreSQL client)

---

## Database setup

Each microservice owns its own database (database-per-service pattern).

### 1. Create the three databases

```bash
psql -U postgres -c "CREATE DATABASE auth_db;"
psql -U postgres -c "CREATE DATABASE business_db;"
psql -U postgres -c "CREATE DATABASE rag_db;"
```

On macOS with Homebrew PostgreSQL, you may use your OS user instead of `postgres`:

```bash
createdb auth_db
createdb business_db
createdb rag_db
```

### 2. Create tables (schemas)

From the project root:

```bash
psql -d auth_db     -f database/auth_db/schema.sql
psql -d business_db -f database/business_db/schema.sql
psql -d rag_db      -f database/rag_db/schema.sql
```

| Database | Tables |
|----------|--------|
| `auth_db` | `users`, `roles`, `user_roles`, `oauth_accounts`, `refresh_tokens` |
| `business_db` | `customers`, `products`, `orders`, `order_items` |
| `rag_db` | `documents`, `document_chunks` (with `vector` column) |

> `rag_db` requires the **pgvector** extension. Install it for your PostgreSQL version if `CREATE EXTENSION vector` fails.

### 3. Seed sample data

```bash
psql -d auth_db     -f database/auth_db/seed.sql
psql -d business_db -f database/business_db/seed.sql
psql -d rag_db      -f database/rag_db/seed.sql
```

This creates:
- **500 users** (`user1@example.com` … `user500@example.com`) with placeholder password hashes
- **500 customers** linked to those users (deterministic UUIDs)
- **1000 products**, **3000 orders**, order line items
- RAG document metadata rows

**Note:** Seed users use `fake_hash_*` passwords — login will not work until you set a real bcrypt hash. Guest chat still works for policy/product questions.

### 4. Ingest RAG documents (vectors)

SQL seed only adds document metadata. Chunks and embeddings are created by the RAG service:

```bash
# Optional: regenerate PDFs from text files in backend/documents/content/
cd backend/rag-service
source .venv/bin/activate
pip install -e ../packages/contracts -r requirements.txt
python -m app.scripts.generate_policy_pdfs

# Chunk, embed, and store in rag_db
python -m app.seeders.knowledge_seeder
```

Requires `OPENAI_API_KEY` and `DATABASE_URL` in `backend/rag-service/.env`.

---

## Environment variables

Copy each service's `.env.example` to `.env` and fill in values.

```bash
cp backend/auth-service/.env.example     backend/auth-service/.env
cp backend/business-service/.env.example backend/business-service/.env
cp backend/rag-service/.env.example      backend/rag-service/.env
cp backend/agent-service/.env.example  backend/agent-service/.env
cp backend/api-gateway/.env.example    backend/api-gateway/.env
cp frontend/.env.example               frontend/.env
```

**Important:** use the **same** `INTERNAL_SERVICE_API_KEY` in gateway, agent, business, and rag services.

| Service | Required variables |
|---------|-------------------|
| auth-service | `DATABASE_URL`, `JWT_SECRET_KEY` |
| business-service | `DATABASE_URL`, `INTERNAL_SERVICE_API_KEY` |
| rag-service | `DATABASE_URL`, `OPENAI_API_KEY`, `INTERNAL_SERVICE_API_KEY` |
| agent-service | `RAG_SERVICE_URL`, `BUSINESS_SERVICE_URL`, `INTERNAL_SERVICE_API_KEY` |
| api-gateway | `AUTH_SERVICE_URL`, `AGENT_SERVICE_URL`, `INTERNAL_SERVICE_API_KEY` |
| frontend | `VITE_API_URL=http://localhost:8000` |

Example database URLs (adjust user/password/host to your setup):

```
# auth-service/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/auth_db

# business-service/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/business_db

# rag-service/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag_db
```

---

## Running the backend

### Option A — start script (recommended)

Starts all five services in the background and writes logs to `logs/`:

```bash
./scripts/dev-start.sh
```

Stop everything:

```bash
./scripts/dev-stop.sh
```

Follow logs:

```bash
tail -f logs/gateway.log logs/agent.log
```

### Option B — manual (one terminal per service)

Each service has its own virtualenv and dependencies:

```bash
cd backend/auth-service && source .venv/bin/activate
pip install -e ../packages/contracts -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Repeat for:

| Service | Directory | Port |
|---------|-----------|------|
| Business | `backend/business-service` | 8003 |
| RAG | `backend/rag-service` | 8002 |
| Agent | `backend/agent-service` | 8004 |
| Gateway | `backend/api-gateway` | 8000 |

**Start order:** auth and business can start in any order; RAG needs `rag_db`; agent needs business + RAG URLs; gateway needs auth + agent.

### Health checks

```bash
curl http://localhost:8000/health          # gateway
curl http://localhost:8001/health          # auth
curl http://localhost:8002/health          # rag
curl http://localhost:8003/health          # business
curl http://localhost:8004/health          # agent
```

---

## Running the frontend

```bash
cd frontend
npm install
cp .env.example .env    # if you have not already
npm run dev
```

Open **http://localhost:5173**

- **Guest mode:** policy, FAQ, and product questions work without login.
- **Signed in:** order status uses your JWT; orders are scoped to your customer profile.

---

## Project structure

```
e-commerce-ai-agent/
├── backend/
│   ├── api-gateway/          # Public API (port 8000)
│   ├── auth-service/         # Auth + JWT (8001)
│   ├── rag-service/          # RAG pipeline (8002)
│   ├── business-service/     # Products & orders (8003)
│   ├── agent-service/        # Intent + orchestration (8004)
│   ├── packages/contracts/   # Shared Pydantic models
│   └── documents/            # Policy PDFs + content/*.txt
├── frontend/                 # React + Vite UI
├── database/
│   ├── auth_db/              # schema.sql, seed.sql
│   ├── business_db/
│   └── rag_db/
├── scripts/
│   ├── dev-start.sh
│   └── dev-stop.sh
└── logs/                     # Service logs (created by dev-start)
```

---

## API overview (via gateway)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/login` | Login → JWT |
| `GET` | `/api/auth/me` | Current user (Bearer token) |
| `POST` | `/api/chat` | Send message to AI agent |

Example chat request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your refund policy?"}'
```

With authentication:

```bash
TOKEN="..."   # from /api/auth/login
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Where is my order #1?"}'
```

---

## Example chat prompts

| Question | Routed to |
|----------|-----------|
| "Where is my order #1?" | Business service (requires login) |
| "What is your refund policy?" | RAG |
| "How long does shipping take?" | RAG (shipping policy) |
| "Do you accept PayPal?" | RAG (payment policy) |
| "Do you have shoes in stock?" | Business product search |

---

## Roadmap (next steps)

1. **Demo user** — one account with a real bcrypt password for easy login testing
2. **My orders** — list all orders for the logged-in customer
3. **LLM intent detection** — replace keyword routing with OpenAI classification
4. **Docker Compose** — PostgreSQL + all services in one command
5. **LangGraph** — multi-step agent flows (optional)

---

## License

TBD
