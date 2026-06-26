# Business AI Agent

An AI system that helps small businesses answer customer questions, analyze complaints, check orders, summarize sales issues, and recommend actions.

This is not just a chatbot — it is a small **AI employee** that uses real company data. RAG (retrieval-augmented generation) will ground answers in business documents and records instead of guesses.

Works for e-commerce stores, restaurants, gyms, sports booking businesses, and similar operations.

## Problem it solves

Small businesses lose time answering the same questions:

- "Where is my order?"
- "Can I refund this?"
- "What are today's offers?"
- "Why are customers complaining?"
- "Which products are causing problems?"
- "What should I restock?"

## Current status

**Phase 1 (done):** Python project scaffold with OpenAI integration and a simple CLI.

**Phase 1b (done):** PostgreSQL via Docker + SQLAlchemy connection layer.

**Next:** Add database schema, sample business data, and RAG so the agent answers from real records.

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install the project

```bash
pip install -e .
```

### 3. Configure OpenAI

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Start PostgreSQL

The easiest way for local development is Docker:

```bash
docker compose up -d
```

This starts PostgreSQL 16 with:

| Setting  | Value            |
|----------|------------------|
| Host     | `localhost`      |
| Port     | `5432`           |
| Database | `business_agent` |
| User     | `business_agent` |
| Password | `business_agent` |

Add the database URL to `.env` (already in `.env.example`):

```
DATABASE_URL=postgresql+psycopg://business_agent:business_agent@localhost:5432/business_agent
```

Verify the connection:

```bash
business-agent db check
```

You should see `PostgreSQL connection OK` plus the server version.

#### Without Docker

Install PostgreSQL locally, then create the database and user:

```sql
CREATE USER business_agent WITH PASSWORD 'business_agent';
CREATE DATABASE business_agent OWNER business_agent;
```

Point `DATABASE_URL` in `.env` at your instance.

### 5. Run the agent

```bash
business-agent ask "What should I restock this week?"
```

Or the shorthand (still supported):

```bash
business-agent "What should I restock this week?"
```

## Project structure

```
e-commerce-ai-agent/
├── data/                    # Static files (exports, docs for RAG)
├── docker-compose.yml       # Local PostgreSQL
├── src/
│   └── business_agent/
│       ├── __main__.py      # CLI entry point
│       ├── agent.py         # Agent logic and system prompt
│       ├── config.py        # Settings (API key, model, database URL)
│       ├── db/
│       │   ├── base.py      # SQLAlchemy declarative base
│       │   └── session.py   # Engine, sessions, connection check
│       └── llm/
│           └── client.py    # OpenAI client wrapper
├── .env.example
├── pyproject.toml
└── README.md
```

## Roadmap

1. **Project setup** — Python package, OpenAI LLM, CLI
2. **PostgreSQL** — Docker Compose, SQLAlchemy connection
3. **Database schema** — Orders, products, complaints, customers tables
4. **RAG pipeline** — Embed and retrieve business data before generating answers
5. **Tools** — Structured lookups (order by ID, complaint trends, restock suggestions)
6. **Interface** — Web or chat UI for staff and customers

## License

TBD
