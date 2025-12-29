# A.B.E.L - Guide de Deploiement Securise

## Pre-requis

- Serveur avec Docker et Docker Compose
- Reverse proxy (nginx/traefik)
- Certificat SSL/TLS valide
- Gestionnaire de secrets (optionnel mais recommande)

## Etape 1: Configuration des Secrets

### 1.1 Generer les Secrets

```bash
# SECRET_KEY (32+ caracteres)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Ou avec OpenSSL
openssl rand -base64 32
```

### 1.2 Creer le fichier .env de production

```bash
cd backend

# Copier l'exemple
cp .env.example .env

# Editer avec vos vraies valeurs
nano .env
```

**Contenu minimum pour production:**

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=<genere-avec-python-secrets>
APP_NAME=A.B.E.L
API_VERSION=v1

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/abel_db

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=abel_memories

# OpenAI (requis pour chat)
OPENAI_API_KEY=<votre-cle>
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ElevenLabs (requis pour TTS)
ELEVENLABS_API_KEY=<votre-cle>
ELEVENLABS_VOICE_ID=<votre-voice-id>

# Google (optionnel)
GOOGLE_CLIENT_ID=<votre-client-id>
GOOGLE_CLIENT_SECRET=<votre-client-secret>
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/google/callback

# CORS (ajuster selon votre frontend)
CORS_ORIGINS=https://your-frontend.com

# Logging
LOG_LEVEL=INFO
```

### 1.3 Securiser le fichier .env

```bash
# Permissions restrictives
chmod 600 .env

# Verifier que .env est dans .gitignore
grep "^\.env$" ../.gitignore
```

## Etape 2: Valider la Configuration

```bash
# Valider la securite
python scripts/validate_security.py

# Tous les tests doivent PASS
# [PASS] chat.py
# [PASS] voice.py
# [PASS] memory.py
# [PASS] health.py
# [PASS] main.py (docs)
# [PASS] main.py (headers)
# [PASS] config.py
# [PASS] deps.py
```

## Etape 3: Configuration Docker

### 3.1 docker-compose.production.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - abel_network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - abel_network

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
    networks:
      - abel_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
      - qdrant
    restart: unless-stopped
    networks:
      - abel_network
    # NE PAS exposer directement
    # Utiliser reverse proxy

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - abel_network

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

networks:
  abel_network:
    driver: bridge
```

### 3.2 Configuration Nginx

**nginx/nginx.conf:**

```nginx
# Upstream backend
upstream backend {
    server backend:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers (en plus de ceux de l'app)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Client body size
    client_max_body_size 25M;

    # Proxy to backend
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
}
```

## Etape 4: Deploiement

### 4.1 Premiere installation

```bash
# 1. Cloner le repo (sur le serveur)
git clone https://github.com/your-org/abel.git
cd abel

# 2. Configurer .env
cp backend/.env.example backend/.env
nano backend/.env  # Editer avec vraies valeurs

# 3. Valider
cd backend
python scripts/validate_security.py

# 4. Build et lancer
cd ..
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# 5. Verifier les logs
docker-compose -f docker-compose.production.yml logs -f backend

# 6. Initialiser la DB
docker-compose -f docker-compose.production.yml exec backend \
  poetry run alembic upgrade head

# 7. Creer un utilisateur admin (si auth implementee)
docker-compose -f docker-compose.production.yml exec backend \
  poetry run python scripts/create_admin.py
```

### 4.2 Mise a jour

```bash
# 1. Pull les changements
git pull origin main

# 2. Rebuild
docker-compose -f docker-compose.production.yml build backend

# 3. Relancer (avec zero downtime)
docker-compose -f docker-compose.production.yml up -d --no-deps backend

# 4. Verifier
docker-compose -f docker-compose.production.yml logs -f backend

# 5. Migrations DB si necessaire
docker-compose -f docker-compose.production.yml exec backend \
  poetry run alembic upgrade head
```

## Etape 5: Verification Post-Deploiement

### 5.1 Tests de base

```bash
# Health check
curl https://your-domain.com/health
# {"status":"ABEL ONLINE","timestamp":"..."}

# Verifier que /docs n'est PAS accessible
curl -I https://your-domain.com/docs
# HTTP/1.1 404 Not Found

# Verifier security headers
curl -I https://your-domain.com/
# Doit inclure X-Frame-Options, CSP, etc.
```

### 5.2 Tests de securite

```bash
# Test erreur generique (pas de details)
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
# {"detail":"An error occurred"}  <- Generique

# Test rate limiting
for i in {1..100}; do
  curl -s https://your-domain.com/health > /dev/null
done
# Devrait etre limite apres X requetes
```

### 5.3 Tests fonctionnels

```bash
# Chat basique
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'

# Health detaille
curl https://your-domain.com/health/detailed
```

## Etape 6: Monitoring et Maintenance

### 6.1 Monitoring

```bash
# Logs en temps reel
docker-compose -f docker-compose.production.yml logs -f

# Metriques des containers
docker stats

# Health checks automatiques
# Ajouter dans crontab:
*/5 * * * * curl -f https://your-domain.com/health || alert-script.sh
```

### 6.2 Backups

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres \
  pg_dump -U abel abel_db > backup_$(date +%Y%m%d).sql

# Backup Qdrant
docker-compose -f docker-compose.production.yml exec qdrant \
  tar -czf /backup/qdrant_$(date +%Y%m%d).tar.gz /qdrant/storage

# Script automatise (crontab)
0 2 * * * /path/to/backup-script.sh
```

### 6.3 Mise a jour des dependances

```bash
# Backend
docker-compose -f docker-compose.production.yml exec backend \
  poetry update

# Rebuild avec nouvelles deps
docker-compose -f docker-compose.production.yml build backend
docker-compose -f docker-compose.production.yml up -d backend
```

## Etape 7: Troubleshooting

### Probleme: L'app ne demarre pas

```bash
# Verifier les logs
docker-compose -f docker-compose.production.yml logs backend

# Erreur commune: SECRET_KEY manquant
# -> Verifier .env

# Erreur commune: DB inaccessible
# -> Verifier que postgres est up
docker-compose -f docker-compose.production.yml ps postgres
```

### Probleme: Erreurs 500

```bash
# Logs backend
docker-compose -f docker-compose.production.yml logs backend | grep ERROR

# Les details sont dans les logs (securise)
# Pas exposes aux clients (securise)
```

### Probleme: Rate limiting trop strict

```bash
# Ajuster dans nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

# Recharger nginx
docker-compose -f docker-compose.production.yml restart nginx
```

## Checklist Finale

Avant de declarer la production prete:

- [ ] SECRET_KEY genere et configure (32+ caracteres)
- [ ] DATABASE_URL configure avec credentials forts
- [ ] APP_ENV=production
- [ ] DEBUG=false
- [ ] HTTPS configure avec certificat valide
- [ ] Security headers presents (tester avec curl -I)
- [ ] /docs inaccessible en production
- [ ] Rate limiting configure
- [ ] Backups automatiques configures
- [ ] Monitoring en place (logs, alertes)
- [ ] Tests de securite passes
- [ ] Documentation a jour
- [ ] Equipe formee aux procedures

## Ressources

- [OWASP Top 10](https://owasp.org/Top10/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)

## Support

Pour toute question ou probleme de securite, contacter l'equipe de developpement.

**IMPORTANT**: En cas de faille de securite detectee, suivre la procedure de divulgation responsable.
