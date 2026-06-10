# RailRide Super App

RailRide is a production-ready cross-platform super app that unifies **Indian Railway services** and **ride booking** (Bike, Auto, Taxi) into a single mobile experience, backed by a scalable FastAPI backend and web admin dashboard.

## Monorepo Structure

```
railride/
├── mobile/          # Flutter app (Android + iOS)
├── backend/         # FastAPI + PostgreSQL + Redis
├── admin/           # React admin dashboard
├── docs/            # Architecture, API, deployment guides
└── docker-compose.yml
```

## Features

### Mobile App (Flutter)
- Train search, PNR status, live train status, schedules, station search, favorites
- Bike / Auto / Taxi booking with fare estimate and Google Maps live tracking
- Wallet, UPI payments, trip history, push notifications (FCM)
- Mobile & email login with OTP, JWT refresh tokens
- Dark / light theme, Material 3 UI

### Backend (FastAPI)
- REST APIs with Swagger at `/docs`
- JWT authentication with refresh tokens
- WebSocket real-time driver tracking
- Redis caching for railway data
- PostgreSQL with Alembic migrations

### Admin Dashboard (React)
- User & driver management
- Live ride monitoring
- Revenue analytics
- Notification & complaint management

## Quick Start (Docker)

```bash
# From project root
cp backend/.env.example backend/.env
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Admin Panel | http://localhost:3001 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### Default Admin Credentials
- **Email:** `admin@railride.com`
- **Password:** `Admin@123`

## Mobile App Setup

```bash
cd mobile
flutter pub get
flutter run
```

1. Set API URL in `lib/core/config/app_config.dart`
2. Add Google Maps API key (AndroidManifest, AppDelegate, app_config)
3. Configure Firebase (`flutterfire configure`) for push notifications
4. Use **"Continue as Demo User"** on login to explore without backend

## Admin Panel Setup

```bash
cd admin
cp .env.example .env
npm install
npm run dev
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — system design and data flow
- [API Reference](docs/API.md) — endpoint overview
- [Deployment Guide](docs/DEPLOYMENT.md) — AWS EC2, RDS, S3, production setup

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Mobile | Flutter, Riverpod, go_router, Google Maps, Firebase |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Redis, WebSockets |
| Admin | React, Vite, TypeScript, Recharts |
| Cloud | AWS EC2, RDS, S3, Firebase Cloud Messaging |
| DevOps | Docker, Docker Compose, Alembic |

## License

Proprietary — RailRide © 2026
