# RealBehind Hostinger VPS Deployment

Ziel: Railway-FastAPI-App als Docker-Compose-Service auf dem Hostinger VPS betreiben und per Caddy ausliefern.

## Voraussetzungen

- DNS `A` Records für `realbehind.com` und `www.realbehind.com` zeigen auf `187.124.40.126`
- SSH-Zugriff auf `root@187.124.40.126`
- frische Secrets:
  - `GOOGLE_API_KEY`
  - `GEMINI_MODEL`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `NOTIFICATION_EMAIL`
  - `LEADS_DB_PATH` (Default im Docker-Deploy: `/app/data/leads.db`)

## Deploy

Vor dem VPS-Deploy müssen diese Deployment-Dateien committed und nach GitHub gepusht sein, damit der Server-Clone sie enthält.

```bash
ssh root@187.124.40.126
docker network create web || true
mkdir -p /root/realbehind-funnel
cd /root/realbehind-funnel
git clone https://github.com/dan007niel-sudo/realbehind-funnel.git .
cp .env.example .env
nano .env
docker compose up -d --build
curl http://127.0.0.1:8010/health
```

Nach einem bestehenden Setup läuft der Deploy reproduzierbar über:

```bash
ssh root@187.124.40.126
cd /root/realbehind-funnel
./deploy.sh
```

Der Container nutzt `./data:/app/data`, damit Leads und Tracking-Events in SQLite Deploys überleben.

## Caddy

Auf dem VPS läuft Caddy bereits im SVT/Ecclesia-Compose-Projekt. Dieser Caddy muss im gemeinsamen Docker-Netzwerk `web` hängen.

Im bestehenden `/root/svt-technik-bot/docker-compose.yml` beim `caddy` Service ergänzen:

```yaml
services:
  caddy:
    networks:
      - default
      - web

networks:
  web:
    external: true
```

Dann den Block aus `Caddyfile` in `/root/svt-technik-bot/Caddyfile` übernehmen:

```caddy
realbehind.com, www.realbehind.com {
    encode zstd gzip
    reverse_proxy realbehind-funnel:8000
}
```

Anschließend Caddy neu starten:

```bash
cd /root/svt-technik-bot
docker compose up -d caddy
```

Wichtig: Es darf nicht noch ein zweiter Caddy-Container Port 80/443 binden.

## Checks

```bash
curl https://realbehind.com/health
docker compose logs -f realbehind
```

Optional prüfen:

```bash
sqlite3 /root/realbehind-funnel/data/leads.db 'select id, name, status, created_at from leads order by id desc limit 5;'
sqlite3 /root/realbehind-funnel/data/leads.db 'select event, session_id, created_at from tracking_events order by id desc limit 10;'
```

Danach im Funnel einen Testlead mit Pamela-freundlichen Testdaten abschicken und prüfen, ob die E-Mail ankommt.
