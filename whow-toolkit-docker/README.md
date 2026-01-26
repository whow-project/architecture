# WHOW Toolkit - Docker Deployment

This directory contains the Docker image definition for the WHOW Toolkit service. The parent directory (`whow-toolkit-docker/`) provides the full Docker Compose stack that orchestrates the toolkit alongside Virtuoso, Airflow, PostgreSQL, and Redis.


| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| **toolkit** | Custom (Python 3.8) | 5000, 8765 | WHOW Toolkit REST API, WebSocket server, and web UI |
| **virtuoso** | openlink/virtuoso-opensource-7 | 8890, 1111 | RDF triplestore with SPARQL endpoint |
| **airflow-webserver** | apache/airflow:2.6.3-python3.9 | 8080 | Airflow web UI for DAG management |
| **airflow-scheduler** | apache/airflow:2.6.3-python3.9 | - | DAG scheduling and task dispatch |
| **airflow-worker** | apache/airflow:2.6.3-python3.9 | - | Celery workers for task execution |
| **airflow-triggerer** | apache/airflow:2.6.3-python3.9 | - | Event-driven task triggering |
| **flower** | apache/airflow:2.6.3-python3.9 | 5555 | Celery monitoring dashboard |
| **postgres** | postgres:13 | - | Airflow metadata database |
| **redis** | redis:latest | - | Celery message broker |

## Prerequisites

- Docker Engine (20.10+)
- Docker Compose (v2)
- At least 4 GB RAM available for Docker
- At least 2 CPUs
- At least 10 GB free disk space

## Getting Started

### 1. Build and start all services

```bash
cd whow-toolkit-docker
docker compose build
docker compose up -d
```

### 2. Verify services are running

```bash
docker compose ps
```

### 3. Access the services

| URL | Service |
|-----|---------|
| http://localhost:5000 | WHOW Toolkit web UI |
| http://localhost:8080 | Airflow web UI |
| http://localhost:8890 | Virtuoso SPARQL endpoint |
| http://localhost:5555 | Flower (Celery monitor) |

### 4. Default credentials

| Service | Username | Password |
|---------|----------|----------|
| Airflow | `airflow` | `airflow` |
| Virtuoso | `dba` | `dba` |

## Toolkit Docker Image

The toolkit container (`toolkit/Dockerfile`) is built from `python:3.8-slim`:

- Installs `git` and `unixodbc` (for Virtuoso ODBC connectivity)
- Installs Python dependencies from `requirements.txt`
- Installs `pyRML` from the GitHub repository
- Copies the `WHOWToolkit` application code
- Configures Virtuoso ODBC drivers and SSL libraries
- Exposes ports 5000 (HTTP) and 8765 (WebSocket)
- Runs `whow-tk.py` as the entry point

## Airflow Docker Image

The Airflow containers (`Dockerfile` in the root) extend `apache/airflow:2.6.3-python3.9`:

- Installs `python3-pyqt5` and `git`
- Installs shared Python dependencies
- Installs `pyRML` for RDF mapping support within DAGs
- Uses CeleryExecutor with Redis as the broker

## Volume Mounts

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| `postgres-db-volume` | `/var/lib/postgresql/data` | PostgreSQL persistent storage |
| `virtuoso-graphs` | `/graphs` | Shared RDF graph storage between toolkit and Virtuoso |
| `./virtuoso/database` | `/database` | Virtuoso database files |
| `./toolkit/logs` | `/WHOWToolkit/logs` | Toolkit application logs |
| `./dagfactory/dags/` | `/WHOWToolkit/dagfactory/dags` | Generated Airflow DAG files |
| `./dags` | `/opt/airflow/dags` | Airflow DAG directory |
| `./logs` | `/opt/airflow/logs` | Airflow task logs |
| `./plugins` | `/opt/airflow/plugins` | Airflow plugins |

The `virtuoso-graphs` volume is shared between the toolkit and Virtuoso containers, allowing the toolkit to write RDF graph files that Virtuoso can bulk-load.

## Environment Variables

### Airflow Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRFLOW__CORE__EXECUTOR` | `CeleryExecutor` | Task execution backend |
| `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` | `postgresql+psycopg2://airflow:airflow@postgres/airflow` | Database connection |
| `AIRFLOW__CELERY__BROKER_URL` | `redis://:@redis:6379/0` | Redis broker URL |
| `AIRFLOW__CORE__LOAD_EXAMPLES` | `false` | Disable example DAGs |
| `AIRFLOW__API__AUTH_BACKENDS` | `airflow.api.auth.backend.basic_auth` | API authentication |
| `AIRFLOW_UID` | `50000` | User ID in Airflow containers |

### Virtuoso Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DBA_PASSWORD` | `dba` | Virtuoso admin password |

## Common Operations

### View logs

```bash
# Toolkit logs
docker compose logs -f toolkit

# Airflow scheduler logs
docker compose logs -f airflow-scheduler

# All services
docker compose logs -f
```

### Restart a single service

```bash
docker compose restart toolkit
```

### Stop all services

```bash
docker compose down
```

### Stop and remove all data

```bash
docker compose down -v
```

### Access the Airflow CLI

```bash
docker compose run --rm airflow-cli bash
```

### Access the Virtuoso ISQL console

```bash
docker compose exec virtuoso isql 1111 dba dba
```

### Rebuild after code changes

```bash
docker compose build toolkit
docker compose up -d toolkit
```

## Network

All services share a Docker network, enabling inter-service communication by hostname. The toolkit references Airflow as `host.docker.internal:8080` for DAG management API calls.

