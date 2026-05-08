# Grombalia Scout Group - Data Platform

Full-stack web application with role-based access control.

## Stack

- **Frontend**: Angular 17
- **Backend**: FastAPI
- **Database**: PostgreSQL (with RLS)
- **Auth**: JWT
- **ML**: MLflow
- **Monitoring**: Prometheus + Grafana

## Getting Started

### Prerequisites

- Docker & Docker Compose

### Run the Application

```bash
docker-compose up -d --build
```

### Services

| Service       | URL                      |
|---------------|--------------------------|
| Frontend      | http://localhost:4200    |
| Backend API   | http://localhost:8000    |
| API Docs      | http://localhost:8000/docs |
| MLflow        | http://localhost:5000    |
| Prometheus    | http://localhost:9090    |
| Grafana       | http://localhost:3000    |

### Demo Credentials

| Role          | Username      | Password |
|---------------|---------------|----------|
| Group Leader  | group_leader  | password |
| Treasurer     | treasurer     | password |
| Unit Leader   | unit_leader   | password |

## Project Structure

```
grombalia-scout-platform/
├── backend/          # FastAPI backend
├── frontend/         # Angular frontend
├── database/         # PostgreSQL schema
├── prometheus/       # Prometheus config
├── grafana/          # Grafana provisioning
└── docker-compose.yml
```
