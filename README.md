# OpsPilot — Enterprise Agentic AI Operations Assistant

OpsPilot is a portfolio-grade Agentic AI application that turns a natural-language operations request into a controlled multi-step workflow.

It demonstrates:
- LangGraph agent orchestration
- Planner → RAG Research → Tool Execution → Reviewer → Finalizer workflow
- Human-in-the-loop approval for sensitive actions
- RAG over an internal Markdown knowledge base
- Structured tool calling
- FastAPI REST backend
- React + TypeScript frontend
- PostgreSQL persistence and audit events
- Docker Compose
- Automated tests and GitHub Actions CI
- OpenAI-compatible LLM integration
- Deterministic mock mode for demos without an API key

## What the project is about

Imagine an internal engineering operations team receives:

> "The payments API is reporting elevated latency. Check the runbook, inspect the current incident status, and recommend the next steps. Don't execute anything without approval."

OpsPilot decomposes the request, retrieves relevant operational knowledge, calls approved tools, reviews the evidence, and presents a structured recommendation. Consequential actions can pause for explicit human approval.

## Architecture

```text
React + TypeScript UI
        │ REST
        ▼
      FastAPI
        │
        ▼
 LangGraph workflow
 ┌───────────────┐
 │ Planner       │
 │      ↓        │
 │ RAG Research  │
 │      ↓        │
 │ Tool Executor │──────► Incident tools
 │      ↓        │
 │ Reviewer      │
 │      ↓        │
 │ Finalizer     │
 └───────────────┘
        │
   PostgreSQL audit
        │
 Knowledge Base + RAG
```

## Repository structure

```text
opspilot-agentic-ai/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── rag/
│   │   ├── tools/
│   │   └── main.py
│   ├── tests/
│   ├── data/knowledge_base/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── data/knowledge_base/
├── .github/workflows/ci.yml
├── .env.example
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

The default `MOCK_MODE=true` lets you run the complete UI and workflow without an LLM API key. Set `MOCK_MODE=false` and provide `OPENAI_API_KEY` for real model calls.

## Example prompts

```text
Investigate the payments API latency incident and recommend next steps.
```

```text
Investigate the authentication service incident and prepare a remediation plan.
```

```text
Restart the payments service if the runbook says it is appropriate. Ask for approval first.
```

## Agent workflow

### Planner
Turns the request into a structured plan.

### RAG Researcher
Retrieves relevant internal runbooks from the knowledge base.

### Tool Executor
Uses explicitly defined operations tools. Sensitive actions are gated by approval.

### Reviewer
Checks that evidence and tool output are sufficient before the final response.

### Finalizer
Returns a structured response with incident context, evidence, recommendation, and approval state.

## Human-in-the-loop

OpsPilot does not blindly execute consequential operations. A request such as a production restart can return `approval_required`; the frontend then exposes Approve / Reject controls.

## API

`GET /health`

`POST /api/runs`

```json
{"message":"Investigate the payments API latency incident."}
```

`POST /api/runs/{thread_id}/approve`

`POST /api/runs/{thread_id}/reject`

`GET /api/runs/{thread_id}/events`

## Interview topics demonstrated

Be prepared to explain:
1. Why LangGraph instead of one LLM call?
2. How state moves between graph nodes.
3. Why planning, retrieval, execution, review and finalization are separate.
4. How RAG grounds an agent in internal knowledge.
5. How tool permissions and human approval reduce unsafe execution.
6. How you would add durable graph checkpoints in production.
7. How you would defend against prompt injection in retrieved documents.
8. How you would evaluate agent quality, tool success, latency and cost.

## Portfolio wording

**OpsPilot — Enterprise Agentic AI Operations Assistant**

> Built a LangGraph-based Agentic AI operations assistant using FastAPI, RAG, tool calling and human-in-the-loop controls; implemented planning, knowledge retrieval, incident investigation, review and structured response generation with PostgreSQL audit logging, Docker and CI.

Only claim infrastructure you have actually deployed or tested.

## Production hardening roadmap

This is a portfolio/demo system. For production, add real authentication/SSO, durable LangGraph checkpointing, tool-level authorization, secrets management, rate limiting, prompt-injection defenses, tracing/observability, evaluation datasets, background workers, and a managed vector database.

## Vector RAG setup
OpsPilot now uses PostgreSQL + pgvector for semantic retrieval. Knowledge-base Markdown files are chunked, embedded with `text-embedding-3-small`, and stored in `rag_documents`.

1. Put `OPENAI_API_KEY=...` in `.env`.
2. Start the stack: `docker compose up --build -d`.
3. Index the knowledge base: `docker compose exec backend python -m app.rag.ingest`.
4. Verify: `curl http://localhost:8000/health` and confirm `vector_store` is `pgvector` and `embeddings_configured` is `true`.

If no OpenAI key is configured, the app remains runnable with fallback retrieval, but it is not semantic vector retrieval until embeddings are indexed.
