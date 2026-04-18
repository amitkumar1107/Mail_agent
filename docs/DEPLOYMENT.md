# Deployment Guide (Oracle Cloud Always Free)

## 1. Provision VM
- Create an Ubuntu VM on Oracle Cloud Always Free.
- Open inbound ports: `22`, `80`, `443`.
- Attach a reserved public IP.

## 2. Install Docker + Compose
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 3. Deploy Project
```bash
git clone <your-repo-url> mail_helper
cd mail_helper
cp .env.example .env
# edit .env with strong secrets, domain, smtp credentials

./infra/scripts/predeploy_check.sh .env
docker compose up -d --build
```

## 4. Verify Stack
```bash
docker compose ps
curl http://localhost/health/live/
curl http://localhost/health/ready/
```

## 5. Domain + SSL (Let's Encrypt, free)
1. Point domain A record to VM public IP.
2. Install host nginx + certbot:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```
3. Configure host nginx to reverse proxy to container nginx (`127.0.0.1:80`) and request cert:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```
4. Ensure auto-renew:
```bash
sudo systemctl status certbot.timer
```

## 6. Recommended Host Nginx Reverse Proxy
- Terminate TLS at host nginx.
- Proxy pass to Docker nginx on port `80`.
- Keep `X-Forwarded-Proto https` so Django secure redirects/cookies work.

## 7. Backups (Postgres)
Manual:
```bash
./infra/scripts/backup_postgres.sh
```
Daily cron (2 AM):
```bash
crontab -e
0 2 * * * cd /home/ubuntu/mail_helper && ./infra/scripts/backup_postgres.sh >> /home/ubuntu/mail_helper/backups/backup.log 2>&1
```
Restore:
```bash
./infra/scripts/restore_postgres.sh ./backups/postgres_mail_assistant_YYYYMMDD_HHMMSS.sql.gz
```

## 8. Rolling Update
```bash
cd /home/ubuntu/mail_helper
git pull
docker compose up -d --build
docker compose ps
```

## 9. Production Checklist
- `DJANGO_DEBUG=False`
- strong `DJANGO_SECRET_KEY`
- correct `DJANGO_ALLOWED_HOSTS`
- correct `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS`
- `SECURE_SSL_REDIRECT=True`
- secure cookies enabled
- `MAIL_SEND_ASYNC=True`
- backups running and tested

## 10. Free-tier Lightweight Mode
If your host cannot run Postgres + Redis + Celery, use:
- `docs/DEPLOY_FREE.md`
- `docker-compose.free.yml`
- `.env.free.example`

This mode trades scalability for easier deployment on constrained free plans.
