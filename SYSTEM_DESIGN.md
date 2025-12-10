# System Design Document
## Task Management System (TAM)

---

## Architecture Overview

**Microservices Architecture** with 7 containerized services:

```
Internet → Nginx (SSL) → Frontend (React SPA)
                       ↓ Backend (FastAPI REST API)
                       ↓ Worker (RQ Background Jobs)
                       ↓ PostgreSQL (Database)
                       ↓ Redis (Cache/Queue)
                       ↓ Dozzle (Log Viewer)
```

**Key Design Principles:**
- Stateless services for horizontal scaling
- Health-based dependency management
- Structured JSON logging for observability
- Security-first (Argon2id, JWT, SSL/TLS, non-root containers)

---

## Technology Stack Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| **Backend** | FastAPI | Modern async framework, automatic API docs, high performance |
| **Frontend** | React + Vite | Industry standard SPA, fast dev experience |
| **Database** | PostgreSQL | ACID compliance, rich features, production-proven |
| **Cache/Queue** | Redis | In-memory speed, simple RQ integration |
| **Worker** | RQ | Python-native, no extra broker needed |
| **Proxy** | Nginx | Industry standard, SSL termination, static file serving |
| **Logging** | Dozzle | Zero-config log viewing, lightweight |

---

## Data Models

### User
```python
id (UUID PK), email (unique), hashed_password, full_name, is_active, created_at, updated_at
```

### Task
```python
id (UUID PK), title, description, priority (low/medium/high), status (pending/in-progress/completed),
created_at, updated_at, user_id (UUID FK)
```

**Relationships:** User → many Tasks (one-to-many)

---

## API Design

**RESTful Endpoints:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT token
- `GET /api/tasks` - List tasks (with optional filters: `?status=pending&priority=high`)
- `GET /api/tasks/search?q=keyword` - Search tasks (BONUS)
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /health` - Health check

**Features:** JWT auth, filtering by status/priority, search by title/description, background notifications

---

## Security

1. **Authentication:** Argon2id (OWASP recommended, GPU-resistant)
2. **Authorization:** JWT tokens, user-scoped queries
3. **Network:** SSL/TLS, internal Docker network, CORS protection
4. **Containers:** Non-root users, minimal base images
5. **Input:** Pydantic validation, SQLAlchemy ORM (SQL injection protection)

---

## Infrastructure

**Docker Multi-Stage Builds:**
- Builder stage (with build tools) → Runtime stage (minimal)
- Reduces image size, attack surface, faster deployments

**Health Checks:**
- All services have health checks
- Dependency chain: db/redis → backend → frontend/worker → nginx
- Graceful degradation and automatic restarts

**Persistence:**
- PostgreSQL data → `postgres_data` volume
- Redis AOF → `redis_data` volume

**Logging:**
- JSON structured logs (ELK/Loki compatible)
- Log rotation (10MB × 3 files per container)
- Centralized viewing via Dozzle

---

## CI/CD Pipeline

**GitHub Actions Workflow:**

1. **Code Quality** - Black, Flake8, ESLint
2. **Tests** - pytest (with Postgres/Redis services), npm test
3. **Build & Push** - Multi-stage Docker images → GitHub Container Registry
4. **Deploy** - SSH/K8s/Cloud (configurable placeholder)

**Triggers:** Push to main/develop, Pull requests to main

---

## Scalability

**Horizontal Scaling:**
- Frontend: Stateless SPA 
- Backend: Stateless API (JWT auth), scale with Docker Swarm/K8s
- Worker: Add replicas to process queue faster
- Database: Read replicas, connection pooling
- Redis: Cluster for HA

**Performance:**
- Async I/O (FastAPI)
- Connection pooling (SQLAlchemy)
- Redis caching
- Nginx static asset caching
- Database indexes on FK and frequently queried fields

---

## Key Trade-offs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Orchestration | Docker Compose | Kubernetes | Simpler for demo, easier to understand |
| Auth | JWT | Sessions | Stateless, horizontal scaling |
| Password Hash | Argon2id | bcrypt | OWASP 2024 recommendation, GPU-resistant |
| Queue | RQ | Celery | Simpler setup, sufficient for scale |
| Logging | Dozzle | ELK/Loki | Zero-config, lightweight |
| Repo | Monorepo | Separate repos | Single version, unified CI/CD |

---

## Production Readiness

**Current State:**
- ✅ Multi-stage builds
- ✅ Health checks & graceful degradation
- ✅ Structured logging
- ✅ SSL/TLS encryption
- ✅ Non-root containers
- ✅ CI/CD pipeline
- ✅ Service dependencies
- ✅ Log rotation


