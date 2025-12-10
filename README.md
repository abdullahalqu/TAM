# Task Management System (TAM)

> A containerized task management application demonstrating DevOps practices, microservices architecture, and full-stack application.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Services & Ports](#services--ports)
- [API Documentation](#api-documentation)
- [Monitoring & Logging](#monitoring--logging)
- [Security](#security)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

This Task Management System is a full-stack application built to demonstrate a modulare architecture. The system implements:

- **RESTful API** with JWT authentication
- **Asynchronous task processing** with background workers
- **Containerized microservices** with Docker
- **Service orchestration** with Docker Compose
- **Centralized logging** and monitoring
- **SSL/TLS encryption** for secure communication
- **Health checks** and graceful degradation

**Use Case**: Users can register, authenticate, and manage tasks (CRUD operations). When tasks are created or updated, the system sends asynchronous notifications through background workers, demonstrating queue-based processing.

### Documentation

- **[README.md](README.md)** (this file) - Quick start, setup, API docs, troubleshooting
- **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)** - Architecture, tech stack rationale, security, scalability, trade-offs
- **[DATABASE_ERD.md](DATABASE_ERD.md)** - Database schema, relationships, indexes, queries

---

## Architecture

**7-Service Microservices Architecture:**
- Nginx (Reverse Proxy + SSL)
- React Frontend (SPA)
- FastAPI Backend (REST API)
- RQ Worker (Background Jobs)
- PostgreSQL (Database)
- Redis (Cache/Queue)
- Dozzle (Log Viewer)

> **See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for detailed architecture diagrams, service communication flows, and design decisions.**

---

## Features

### Application Features
- ✅ User registration and JWT authentication
- ✅ CRUD operations for task management
- ✅ Real-time task status updates
- ✅ notification system
- ✅ Secure password hashing (Argon2id - OWASP recommended)
- ✅ Token-based session management

### DevOps Features
- 🐳 **Containerization**: Multi-stage Docker builds for optimized images
- 🔄 **Orchestration**: Docker Compose with health checks and dependencies
- 📊 **Monitoring**: Centralized logging with Dozzle
- 🔒 **Security**: SSL/TLS encryption, non-root containers, secrets management
- 📝 **Structured Logging**: JSON logs compatible with ELK/Loki/Grafana stacks
- 🚀 **Production-Ready**: Health checks, graceful shutdowns, log rotation
- ⚡ **Performance**: Redis caching, connection pooling, optimized images
- 🔧 **Maintainability**: environment-based configuration

---

## Tech Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Redis, RQ, Pydantic, Argon2id (password hashing)

**Frontend:** React 18, Vite, React Router, Axios

**DevOps:** Docker (multi-stage builds), Docker Compose, Nginx, Dozzle, GitHub Actions CI/CD

> **See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for technology rationale, alternatives considered, and trade-off decisions.**

---

## Prerequisites

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**
- **Ports Available**: 80, 3000, 5432, 6379, 8000, 8080 (443 for HTTPS if enabled)

---

## Quick Start

> **⚠️ Security Note:** This setup uses demo credentials for easy testing. **DO NOT use in production!**
> For production, generate strong secrets: `openssl rand -hex 32` and update `.env`

```bash
# 1. Clone the repository
git clone <repository-url>
cd TAM

# 2. Create environment file (uses demo secrets for quick testing)
cp .env.example .env

# 3. Start all services
docker-compose up --build

# 4. Access the application
# Frontend:        http://localhost
# Backend API:     http://localhost/api
# API Docs:        http://localhost:8000/docs
# Log Viewer:      http://localhost:8080
```

That's it! The application is now running with all services.

---

## Detailed Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_DB=taskdb
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=<your-secure-password>

# Security - IMPORTANT: Generate a new secret key!
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO              # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json             # json (production) | standard (development)
ENVIRONMENT=production      # development | staging | production

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost,http://localhost:80
```

### 2. Build and Run

```bash
# Build images and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

---

## Services & Ports

| Service       | Container Name  | Internal Port | External Port | Description                    |
|---------------|-----------------|---------------|---------------|--------------------------------|
| **Nginx**     | tam-nginx       | 80, 443       | 80, 443       | Reverse proxy, SSL termination |
| **Frontend**  | tam-frontend    | 80            | 3000          | React SPA (via Nginx)          |
| **Backend**   | tam-backend     | 8000          | 8000          | FastAPI REST API               |
| **Worker**    | tam-worker      | -             | -             | RQ background worker           |
| **PostgreSQL**| tam-db          | 5432          | 5432          | Database                       |
| **Redis**     | tam-redis       | 6379          | 6379          | Cache and message queue        |
| **Dozzle**    | tam-logs        | 8080          | 8080          | Log viewer UI                  |

### Service Dependencies

Services start in the correct order using health check conditions:

```
db, redis (start first)
    ↓
backend (waits for db + redis healthy)
    ↓
worker, frontend (wait for backend healthy)
    ↓
nginx (waits for frontend + backend healthy)
```

### Optional: Enable HTTPS

By default, the application runs on HTTP only. To enable HTTPS:

**Step 1: Generate SSL Certificates**

Self-signed certificates are included in `nginx/certs/`. To regenerate:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/localhost.key \
  -out nginx/certs/localhost.crt \
  -subj "/C=SA/ST=Riyadh/L=Riyadh/O=TAM/CN=localhost"
```

**Step 2: Enable HTTPS in nginx/conf.d/app.conf**

Uncomment the entire HTTPS server block (lines 111-216):

```bash
# Edit nginx/conf.d/app.conf and uncomment the HTTPS server block
# Remove the # from each line in the "HTTPS server" section
```

**Step 3: Enable HTTPS in docker-compose.yml**

Uncomment the HTTPS port and certificate volume:

```yaml
# In nginx service configuration:
ports:
  - "${HTTP_PORT:-80}:80"
  - "${HTTPS_PORT:-443}:443"      # Uncomment this line

volumes:
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  - ./nginx/conf.d:/etc/nginx/conf.d:ro
  - ./nginx/certs:/etc/nginx/ssl:ro  # Uncomment this line
```

**Step 4: Restart Services**

```bash
docker-compose down
docker-compose up -d
```

**Access:** https://localhost (accept browser warning for self-signed cert)

> **Production:** Replace self-signed certificates with CA-signed certificates from Let's Encrypt or a certificate authority.

---

## API Documentation

> **Database Schema:** See [DATABASE_ERD.md](DATABASE_ERD.md) for data models, relationships, and indexes.

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-10T12:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=SecurePass123!
```

**Note:** Use email in the `username` field (OAuth2 standard)

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Task Endpoints

#### Create Task
```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Complete documentation",
  "description": "Write comprehensive README",
  "priority": "high",
  "status": "pending"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "title": "Complete documentation",
  "description": "Write comprehensive README",
  "priority": "high",
  "status": "pending",
  "created_at": "2025-01-10T12:00:00Z",
  "updated_at": "2025-01-10T12:00:00Z",
  "user_id": "user-uuid"
}
```

#### List Tasks
```http
GET /api/tasks
Authorization: Bearer <token>

# With filters (optional):
GET /api/tasks?status=pending&priority=high
GET /api/tasks?status=in-progress
GET /api/tasks?priority=low
```

#### Search Tasks (BONUS)
```http
GET /api/tasks/search?q=documentation
Authorization: Bearer <token>
```

#### Get Task
```http
GET /api/tasks/{task_id}
Authorization: Bearer <token>
```

#### Update Task
```http
PATCH /api/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "priority": "medium",
  "status": "completed"
}
```

#### Delete Task
```http
DELETE /api/tasks/{task_id}
Authorization: Bearer <token>
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-10T12:00:00Z"
}
```

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Monitoring & Logging

### Centralized Logging with Dozzle

Access the Dozzle UI at **http://localhost:8080**

Features:
- Real-time log streaming from all containers
- Search and filter logs
- Multi-container view
- No configuration required

### Structured JSON Logging

All services output structured JSON logs compatible with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki + Promtail**

Example log entry:
```json
{
  "timestamp": "2025-01-10T12:00:00.000Z",
  "level": "INFO",
  "service": "backend",
  "environment": "production",
  "message": "User authenticated successfully",
  "request_id": "abc123",
  "user_id": 1,
  "endpoint": "/api/tasks",
  "method": "POST",
  "status_code": 201,
  "duration_ms": 45
}
```

### Log Rotation

Logs are automatically rotated to prevent disk space issues:
- Max size: 10MB per file
- Max files: 3 per container
- Driver: json-file

### Health Checks

All services include health checks:

```bash
# Check all service health
docker-compose ps

# Backend health endpoint
curl http://localhost:8000/health

# PostgreSQL health
docker exec tam-db pg_isready -U taskuser

# Redis health
docker exec tam-redis redis-cli ping
```

---

## Security

**Implemented Measures:**
- JWT authentication with Argon2id password hashing
- SSL/TLS encryption, Docker network isolation, CORS protection
- Non-root containers, multi-stage builds, no hardcoded secrets
- SQL injection protection (ORM), input validation (Pydantic)

**Production Checklist:**
- Generate strong SECRET_KEY (`openssl rand -hex 32`)
- Replace self-signed SSL certificates with CA-signed
- Enable rate limiting, firewall rules, database SSL
- Set up secrets management (AWS Secrets Manager, Vault)
- Configure monitoring, alerting, and backups

> **See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for detailed security architecture and threat modeling.**

---

## Deployment

### Local Development

```bash
# Use development logging format
LOG_FORMAT=standard LOG_LEVEL=DEBUG docker-compose up
```


```

### CI/CD Pipeline

Automated GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

1. **Code Quality** - Black, Flake8, ESLint
2. **Tests** - pytest + npm test (with PostgreSQL/Redis services)
3. **Build & Push** - Docker images → GitHub Container Registry
4. **Deploy** - Configurable 

**Triggers:** Push to main/develop, Pull requests to main

> **See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for complete CI/CD pipeline details and deployment strategies.**

---

## Troubleshooting

### Container Fails to Start

```bash
# Check logs
docker-compose logs <service-name>


# Restart specific service
docker-compose restart <service-name>
```

### Database Connection Issues

```bash
# Verify database is healthy
docker exec tam-db pg_isready -U taskuser

# Check connection from backend
docker exec tam-backend psql $DATABASE_URL -c "SELECT 1"

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port
lsof -i :80
lsof -i :8000

# Kill process or change port in .env
HTTP_PORT=8080 docker-compose up
```

### SSL Certificate Issues

HTTPS is disabled by default. To enable HTTPS, see the **[Optional: Enable HTTPS](#optional-enable-https)** section.

If you enabled HTTPS and encounter certificate errors:

```bash
# Regenerate self-signed certificate
cd nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout localhost.key -out localhost.crt \
  -subj "/C=SA/ST=Riyadh/L=Riyadh/O=TAM/CN=localhost"

# Then restart nginx
docker-compose restart nginx
```

### Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Verify Redis connection
docker exec tam-worker python -c "import redis; r=redis.from_url('redis://redis:6379'); print(r.ping())"

# Restart worker
docker-compose restart worker
```

### Frontend Build Fails

```bash
# Check Node version (requires >=16)
docker run --rm node:20-alpine node --version

# Clear build cache
docker-compose build --no-cache frontend
```

---

## Project Structure

```
TAM/
├── backend/                  # FastAPI backend application
├── frontend/                 # React frontend application
├── nginx/                    # Nginx reverse proxy configuration
├── .github/workflows/        # CI/CD pipeline (GitHub Actions)
├── docker-compose.yml        # Multi-container orchestration
├── .env.example              # Environment variables template
├── README.md                 # Quick start and user guide
├── SYSTEM_DESIGN.md          # Architecture and technical decisions
└── DATABASE_ERD.md           # Database schema and relationships
```

> **For detailed file structure, see [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md).**

---



