# AI Mail Assistant

A Dockerized Django + DRF + Celery + Redis AI mail assistant that supports natural-language commands, email draft generation, preview/confirmation safety flow, reminders, voice transcription, and dashboard insights.

## Production Features
- JWT auth + OTP verification
- Contacts with duplicate prevention and ambiguity handling
- AI parse/generate with retry + fallback + confidence
- Safety flow: parse -> preview -> send/edit/cancel
- Async mail sending via Celery (`MAIL_SEND_ASYNC=True`)
- Reminder scheduler with Celery Beat + idempotency keys
- Voice transcription endpoint (Whisper)
- Redis caching for contact match/dashboard lookups
- Structured JSON logging
- Health endpoints: `/health/live/`, `/health/ready/`

## Quick Start (Full Stack)
```bash
cp .env.example .env
# update secrets, domain origins, and SMTP credentials

./infra/scripts/predeploy_check.sh .env
docker compose up -d --build
curl http://localhost/health/live/
curl http://localhost/health/ready/
```

## Quick Start (Free-Tier Friendly)
```bash
cp .env.free.example .env.free
# update secrets, domain origins, and SMTP credentials

./infra/scripts/predeploy_check.sh .env.free
docker compose -f docker-compose.free.yml --env-file .env.free up -d --build
curl http://localhost/health/live/
curl http://localhost/health/ready/
```

## UI Pages
- `/login/`
- `/command/`
- `/contacts/`
- `/reminders/`
- `/dashboard/`
- `/history/`

## Docs
- `docs/DEPLOYMENT.md`
- `docs/DEPLOY_FREE.md`
- `docs/RUNBOOK.md`
- `docs/ENVIRONMENT.md`
- `docs/API.md`

## Backup Scripts
- `infra/scripts/backup_postgres.sh`
- `infra/scripts/restore_postgres.sh <backup.sql.gz>`
- `infra/scripts/monitor_stack.sh`
