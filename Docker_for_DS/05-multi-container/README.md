# 05 - Multi-Container: Data Science Stack

A full local data science environment using Docker Compose:
- **Jupyter Lab** -- interactive notebooks
- **PostgreSQL** -- relational database
- **pgAdmin** -- database GUI
- **Redis** -- in-memory cache / feature store (optional)

All services are wired together in a single `docker-compose.yml`. Start everything with one command.

---

## What This Section Covers

- Docker Compose for multi-service coordination
- Service networking (containers talk to each other by service name)
- Named volumes for data persistence
- Environment variable management with `.env` files
- Health checks and service dependencies (`depends_on`)

---

## Files in This Section

```
05-multi-container/
|-- README.md               # This file
|-- docker-compose.yml      # Full stack definition
|-- .env.example            # Environment variable template (copy to .env)
|-- init.sql                # SQL to create sample tables on first start
|-- notebooks/              # Jupyter notebooks (persisted)
```

---

## Quick Start

### Step 1: Set Up Environment Variables

```powershell
cd C:\Training\Microsoft\Copilot\Docker_for_DS\05-multi-container

Copy-Item .env.example .env
# Edit .env with your preferred passwords
```

### Step 2: Create Notebooks Folder

```powershell
New-Item -ItemType Directory -Force -Path notebooks
```

### Step 3: Start the Stack

```powershell
docker compose up -d
```

This starts all services in the background. First run takes a few minutes to pull images and initialize the database.

### Step 4: Check Services Are Up

```powershell
docker compose ps
```

Expected output:
```
NAME                STATUS          PORTS
ds-stack-jupyter    Up              0.0.0.0:8888->8888/tcp
ds-stack-postgres   Up (healthy)    0.0.0.0:5432->5432/tcp
ds-stack-pgadmin    Up              0.0.0.0:5050->80/tcp
```

### Step 5: Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Jupyter Lab | http://localhost:8888 | Token from `docker compose logs jupyter` |
| pgAdmin | http://localhost:5050 | From your .env file |
| PostgreSQL (direct) | localhost:5432 | From your .env file |

---

## Connecting Jupyter to PostgreSQL

Inside a Jupyter notebook, connect using the **service name** as the hostname:

```python
import pandas as pd
from sqlalchemy import create_engine, text

# Use the Docker service name "postgres" as hostname -- 
# Docker's internal DNS resolves it to the postgres container
engine = create_engine(
    "postgresql://dsuser:dspassword@postgres:5432/dsdb"
)

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone()[0])

# Load sample data
df = pd.read_sql("SELECT * FROM sample_sales LIMIT 100", engine)
print(df.head())
```

Replace `dsuser`, `dspassword`, `dsdb` with values from your `.env` file.

---

## Docker Networking Explained

Docker Compose creates a private network for all services. Services communicate using **service names** as hostnames:

```
Jupyter container --> "postgres" --> PostgreSQL container
Jupyter container --> "redis"    --> Redis container
```

From OUTSIDE the containers (your browser/terminal), you use `localhost` with the mapped port:
```
Your browser --> localhost:8888 --> Jupyter container
Your browser --> localhost:5050 --> pgAdmin container
```

---

## Stopping and Restarting

```powershell
# Stop all services (keep data volumes)
docker compose stop

# Start again
docker compose start

# Stop and remove containers (keep data volumes)
docker compose down

# Stop and remove EVERYTHING including volumes (DESTROYS DATA)
docker compose down -v

# Restart a single service
docker compose restart jupyter
```

---

## Exercises

### Exercise 1: Basic Connectivity

1. Start the stack
2. Open Jupyter, run the PostgreSQL connection code above
3. Verify the sample tables exist
4. Open pgAdmin and browse the same data

### Exercise 2: ETL in a Notebook

Write a notebook that:
1. Generates a synthetic dataset with pandas
2. Writes it to PostgreSQL with `df.to_sql()`
3. Reads it back with `pd.read_sql()`
4. Runs an aggregation query

### Exercise 3: Service Restart Resilience

1. Write some data to PostgreSQL from Jupyter
2. Run `docker compose restart postgres`
3. Verify the data is still there (it should be -- stored in a named volume)

### Exercise 4: Logs and Debugging

```powershell
# View logs for all services
docker compose logs

# Follow a specific service
docker compose logs -f postgres

# Open a shell in the postgres container
docker compose exec postgres psql -U dsuser -d dsdb
```

---

## Key Takeaways

- Services communicate by name on Docker's internal network
- External access (your browser) uses `localhost:mapped_port`
- Named volumes persist data across container restarts
- `.env` files keep secrets out of `docker-compose.yml`
- `depends_on` with `condition: service_healthy` ensures proper startup order
