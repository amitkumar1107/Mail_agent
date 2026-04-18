# Operations Runbook

## Health Checks
- App: GET /health/
- Compose: docker compose ps
- Scripted monitor:
```bash
./infra/scripts/monitor_stack.sh
```

## Logs
```bash
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f nginx
```

Log rotation is configured in docker-compose with:
- max-size: 10m
- max-file: 3

## Common Incidents

### 1. Web container crash loop
- Check migrations and env values:
```bash
docker compose logs web --tail=200
```
- Validate DB connectivity in .env.

### 2. Email sending fails
- Verify EMAIL_PROVIDER, SMTP host/user/password.
- Check mail_core sent logs endpoint.

### 3. Tasks not running
- Check worker + beat:
```bash
docker compose logs celery_worker --tail=200
docker compose logs celery_beat --tail=200
```

### 4. Nginx 502
- Confirm backend healthy:
```bash
docker compose ps
curl http://localhost:8000/health/
```

## Recovery
```bash
docker compose down
docker compose up -d --build
```

## Rollback
```bash
git checkout <previous-tag-or-commit>
docker compose up -d --build
```
