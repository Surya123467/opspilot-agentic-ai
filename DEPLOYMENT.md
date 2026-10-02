# Deployment Guide

## GitHub

```bash
git init
git add .
git commit -m "Initial OpsPilot agentic AI platform"
git branch -M main
# replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/opspilot-agentic-ai.git
git push -u origin main
```

## Local production-like test

```bash
docker compose up --build
curl http://localhost:8000/health
```

## Backend deployment

Deploy the `backend` Docker service to a Docker-compatible host. Set `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `MOCK_MODE=false`, and `CORS_ORIGINS`.

## Frontend deployment

Deploy `frontend` to Vercel or another static host and set `VITE_API_BASE_URL` to the public backend URL.

## Important

The default demo intentionally uses deterministic mock behavior. Do not commit API keys. For a real LLM demo, configure the environment securely and test the system before presenting it as production-grade.
