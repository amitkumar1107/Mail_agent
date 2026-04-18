# Free Deployment Guide (Low-resource / free-tier friendly)

Use this mode when you deploy on a free host with limited CPU/RAM and no managed Redis/Postgres.

## What this mode changes
- Uses SQLite (`DB_ENGINE=sqlite`)
- Uses local memory cache (`CACHE_BACKEND=locmem`)
- Disables async email queue (`MAIL_SEND_ASYNC=False`)
- Runs without Redis/Celery containers

## 1) Prepare env
```bash
cp .env.free.example .env.free
# edit .env.free with your real domain + SMTP credentials
```

## 2) Validate config before deploy
```bash
./infra/scripts/predeploy_check.sh .env.free
```

## 3) Start stack
```bash
docker compose -f docker-compose.free.yml --env-file .env.free up -d --build
```

## 4) Verify
```bash
docker compose -f docker-compose.free.yml --env-file .env.free ps
curl http://localhost/health/live/
curl http://localhost/health/ready/
```

## 5) Notes
- For production-grade reliability, move to full stack (`docker-compose.yml`) with Postgres + Redis + Celery.
- If your frontend is served separately (Netlify/Vercel), set `VITE_API_URL=https://your-api-domain/api`.
- Keep `DJANGO_DEBUG=False` in deployed environments.
