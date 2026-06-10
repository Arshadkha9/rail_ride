# RailRide Deployment Guide

## Prerequisites

- Docker & Docker Compose (local/staging)
- AWS account (production)
- Domain name with SSL certificate
- Google Maps API key
- Firebase project for FCM

---

## Local Development

```bash
git clone <repo-url>
cd railride
cp backend/.env.example backend/.env
docker compose up --build
```

Verify:
- API health: `curl http://localhost:8000/health`
- Swagger: http://localhost:8000/docs
- Admin: http://localhost:3001

---

## Production — AWS Architecture

```
Internet
    │
    ▼
Route 53 (DNS)
    │
    ▼
CloudFront (optional CDN)
    │
    ▼
Application Load Balancer (HTTPS)
    │
    ├── EC2 Auto Scaling Group (FastAPI + Nginx)
    ├── EC2 (Admin Panel static files)
    │
    ├── RDS PostgreSQL (Multi-AZ)
    ├── ElastiCache Redis
    └── S3 (user uploads, static assets)
```

---

## Step 1: RDS PostgreSQL

1. Create RDS instance: PostgreSQL 15, `db.t3.medium` minimum for production
2. Enable Multi-AZ, automated backups (7-day retention)
3. Security group: allow port 5432 from EC2 security group only
4. Note connection string:
   ```
   postgresql+asyncpg://railride:<password>@<rds-endpoint>:5432/railride
   ```

---

## Step 2: ElastiCache Redis

1. Create Redis 7 cluster (`cache.t3.micro` for start)
2. Security group: allow 6379 from EC2 only
3. Connection: `redis://<elasticache-endpoint>:6379/0`

---

## Step 3: S3 Bucket

```bash
aws s3 mb s3://railride-assets-prod
aws s3api put-bucket-versioning --bucket railride-assets-prod --versioning-configuration Status=Enabled
```

Use for: user avatars, receipt PDFs, admin exports.

Set in `.env`:
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=railride-assets-prod
AWS_REGION=ap-south-1
```

---

## Step 4: EC2 Backend Deployment

### Launch EC2
- AMI: Ubuntu 22.04 LTS
- Instance: `t3.medium` (2 vCPU, 4 GB RAM)
- Security group: 80, 443 from ALB; 22 from your IP

### Install Docker on EC2

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
```

### Deploy

```bash
git clone <repo-url> /opt/railride
cd /opt/railride
cp backend/.env.example backend/.env
# Edit .env with production values (SECRET_KEY, DATABASE_URL, REDIS_URL, CORS)
docker compose -f docker-compose.prod.yml up -d --build
```

### Run Migrations

```bash
docker exec railride_api alembic upgrade head
```

---

## Step 5: Environment Variables (Production)

```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<64-char-random-string>
DATABASE_URL=postgresql+asyncpg://railride:<pass>@<rds>:5432/railride
REDIS_URL=redis://<elasticache>:6379/0
CORS_ORIGINS=["https://admin.railride.com","https://api.railride.com"]
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
AWS_S3_BUCKET=railride-assets-prod
AWS_REGION=ap-south-1
FIREBASE_CREDENTIALS_PATH=/app/firebase-service-account.json
GOOGLE_MAPS_API_KEY=<your-key>
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Step 6: SSL with ALB + ACM

1. Request ACM certificate for `*.railride.com`
2. Create ALB with HTTPS listener (port 443)
3. Target group → EC2 port 8000
4. HTTP listener redirects to HTTPS

---

## Step 7: Flutter Mobile Release

### Android

```bash
cd mobile
flutter build appbundle --release
```

Upload `build/app/outputs/bundle/release/app-release.aab` to Google Play Console.

Configure:
- `android/app/build.gradle` — `applicationId`, signing config
- `google-services.json` from Firebase
- Google Maps API key in `AndroidManifest.xml`

### iOS

```bash
flutter build ipa --release
```

Upload via Xcode / Transporter to App Store Connect.

Configure:
- `GoogleService-Info.plist`
- Maps API key in `AppDelegate.swift`
- Location permissions in `Info.plist`

---

## Step 8: Firebase Cloud Messaging

1. Create Firebase project → add Android & iOS apps
2. Download service account JSON → place on EC2 at `/app/firebase-service-account.json`
3. Run `flutterfire configure` in `mobile/`
4. Backend sends FCM via `firebase-admin` SDK

---

## Step 9: Admin Panel Deployment

Option A — Docker (included):
```bash
docker build -t railride-admin ./admin
docker run -d -p 80:80 --name railride_admin railride-admin
```

Option B — S3 + CloudFront static hosting:
```bash
cd admin && npm run build
aws s3 sync dist/ s3://railride-admin-prod --delete
```

---

## Monitoring & Logging

| Tool | Purpose |
|------|---------|
| CloudWatch | EC2 metrics, RDS performance |
| CloudWatch Logs | Application logs from Docker |
| Sentry | Error tracking (add to FastAPI + Flutter) |
| Uptime Robot | Health check on `/health` |

---

## Backup Strategy

- **RDS:** Automated daily snapshots, 7-day retention
- **S3:** Versioning enabled
- **Redis:** Not persisted for cache; session data is ephemeral

---

## Scaling Checklist

- [ ] ALB + Auto Scaling Group (min 2 EC2 instances)
- [ ] RDS read replica for railway queries
- [ ] ElastiCache cluster mode for Redis
- [ ] WebSocket sticky sessions on ALB
- [ ] CDN for admin static assets
- [ ] Rate limiting via API Gateway or Nginx
