# Docker Mastery Guide

> Complete Docker reference for interviews and daily use

---

## Table of Contents

1. [Docker Fundamentals](#docker-fundamentals)
2. [🎓 BEGINNER'S DEEP DIVE - Read This First!](#-beginners-deep-dive---read-this-first)
3. [Docker Commands Cheatsheet](#docker-commands-cheatsheet)
4. [Dockerfile Deep Dive](#dockerfile-deep-dive)
5. [Docker Compose](#docker-compose)
6. [PostgreSQL in Docker](#postgresql-in-docker)
7. [Redis in Docker](#redis-in-docker)
8. [React App in Docker](#react-app-in-docker)
9. [Django + Postgres + Redis Stack](#django--postgres--redis-stack)
10. [Networking](#networking)
11. [Volumes & Data Persistence](#volumes--data-persistence)
12. [Interview Questions & Answers](#interview-questions--answers)

---

## Docker Fundamentals

### What is Docker?

Docker is a platform for developing, shipping, and running applications in **containers**. Containers are lightweight, standalone, executable packages that include everything needed to run software.

### Key Concepts

| Concept        | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| **Image**      | Read-only template with instructions for creating a container (like a class) |
| **Container**  | Running instance of an image (like an object)                                |
| **Dockerfile** | Text file with instructions to build an image                                |
| **Registry**   | Storage for Docker images (Docker Hub, ECR, GCR)                             |
| **Volume**     | Persistent data storage that survives container restarts                     |
| **Network**    | Communication channel between containers                                     |

### Docker Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Docker Client                       │
│                    (docker CLI)                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     Docker Daemon                        │
│                      (dockerd)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Images   │  │Containers│  │ Networks │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Docker Registry                       │
│                   (Docker Hub, etc.)                     │
└─────────────────────────────────────────────────────────┘
```

### Container vs Virtual Machine

| Feature     | Container          | Virtual Machine |
| ----------- | ------------------ | --------------- |
| Boot Time   | Seconds            | Minutes         |
| Size        | MBs                | GBs             |
| Performance | Near native        | Overhead        |
| Isolation   | Process level      | Full OS         |
| OS          | Shares host kernel | Separate OS     |

---

## 🎓 BEGINNER'S DEEP DIVE - Read This First!

> **If you're feeling overwhelmed, this section is for you.** I'll explain everything like you're learning it for the first time, with analogies you'll never forget.

---

### 🏠 The Big Picture: What Problem Does Docker Solve?

Imagine you built a Django app on your Windows laptop. It works perfectly. You send it to your friend who has a Mac. It crashes. Why?

- Different Python version
- Missing PostgreSQL
- Different file paths
- Missing environment variables

**Docker's solution**: Package your app with EVERYTHING it needs into a "container" - like a shipping container that works the same everywhere.

```
Your Laptop          →  Docker Container  →  Any Server
(Windows, Python 3.9)   (Linux, Python 3.11,   (Works exactly
                         PostgreSQL, etc.)      the same!)
```

---

### 🍳 Analogy: Docker is Like a Food Delivery Kitchen

| Concept            | Kitchen Analogy                                              |
| ------------------ | ------------------------------------------------------------ |
| **Dockerfile**     | Recipe card with step-by-step instructions                   |
| **Image**          | Frozen meal prepared from the recipe (ready to heat)         |
| **Container**      | The heated meal on a plate being served                      |
| **docker build**   | Chef cooking and freezing meals for later                    |
| **docker run**     | Microwave heating the frozen meal                            |
| **Volume**         | Refrigerator (data that survives after meal is eaten)        |
| **docker-compose** | Full restaurant kitchen with multiple chefs working together |

---

### 📄 Line-by-Line: Understanding YOUR Dockerfile

Let's look at your actual project's Dockerfile:

```dockerfile
# Base image
FROM python:3.11-slim
```

**What this means:**

- "Start with a pre-made Linux system that already has Python 3.11 installed"
- `slim` = minimal version (smaller download, ~150MB vs ~900MB for full)
- Think of it as: "Give me a clean laptop with Python already installed"

**Why not just `FROM python`?**

- `python` = latest version (unpredictable)
- `python:3.11-slim` = exact version (reproducible)

---

```dockerfile
# Prevent .pyc files, enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```

**What this means:**

- `ENV` = Set an environment variable (like `export VAR=value` in bash)
- `PYTHONDONTWRITEBYTECODE=1` = Don't create `.pyc` cache files (keeps container clean)
- `PYTHONUNBUFFERED=1` = Print logs immediately (don't buffer them)

**Why we need this:**
Without `PYTHONUNBUFFERED=1`, when your app crashes, you might not see the last log messages because they're stuck in a buffer!

---

```dockerfile
# Set working directory
WORKDIR /app
```

**What this means:**

- "Create a folder called `/app` and `cd` into it"
- All future commands run from this directory
- Like opening a terminal and typing `mkdir /app && cd /app`

---

```dockerfile
# Install netcat for entrypoint health check
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
```

**Let's break this down piece by piece:**

| Part                          | Meaning                                                       |
| ----------------------------- | ------------------------------------------------------------- |
| `RUN`                         | Execute this command while building the image                 |
| `apt-get update`              | Refresh package lists (like "check for latest apps")          |
| `&&`                          | "If previous command succeeded, then do this"                 |
| `apt-get install -y`          | Install package, `-y` = don't ask for confirmation            |
| `netcat-openbsd`              | A tool to check if ports are open (used to wait for database) |
| `rm -rf /var/lib/apt/lists/*` | Delete cache to reduce image size                             |

**Why one line instead of three?**

```dockerfile
# BAD - Creates 3 layers (bigger image)
RUN apt-get update
RUN apt-get install -y netcat-openbsd
RUN rm -rf /var/lib/apt/lists/*

# GOOD - Creates 1 layer (smaller image)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
```

---

```dockerfile
# Install dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

**What this means:**

1. Copy `requirements.txt` from your computer into the container's `/app` folder
2. Install all Python packages listed in it

**Why copy requirements.txt first, before the rest of the code?**

This is a **caching trick**. Docker caches each step. If nothing changed, it uses the cache.

```
Scenario A: You changed your code (views.py)
├── COPY requirements.txt .  ← Cached! (didn't change)
├── RUN pip install ...      ← Cached! (requirements same)
├── COPY . .                 ← Must rebuild (code changed)
└── Total time: 5 seconds

Scenario B: You added a new package to requirements.txt
├── COPY requirements.txt .  ← Must rebuild (changed!)
├── RUN pip install ...      ← Must rebuild (new packages)
├── COPY . .                 ← Must rebuild (depends on above)
└── Total time: 60 seconds
```

**Order matters!** Put things that change rarely at the top.

---

```dockerfile
# Copy project
COPY . .
```

**What this means:**

- Copy EVERYTHING from your project folder into `/app` in the container
- First `.` = source (your computer, relative to Dockerfile location)
- Second `.` = destination (container's WORKDIR, which is `/app`)

---

```dockerfile
# Normalize shell script line endings and make entrypoint executable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
```

**This fixes a Windows-specific problem:**

| Part               | Meaning                                                |
| ------------------ | ------------------------------------------------------ |
| `sed -i 's/\r$//'` | Remove Windows line endings (CRLF → LF)                |
| `chmod +x`         | Make the file executable (give it "permission to run") |

**Why is this needed?**

- Windows saves text files with `\r\n` (CRLF) line endings
- Linux expects `\n` (LF) only
- Without this fix, Linux sees `#!/bin/sh\r` and says "file not found"

---

```dockerfile
EXPOSE 8000
```

**What this means:**

- Documentation that says "this container listens on port 8000"
- **It doesn't actually open the port!** (that's done with `-p 8000:8000`)
- Think of it as a label saying "connect here"

---

```dockerfile
ENTRYPOINT ["/bin/sh", "-c", "sed -i 's/\r$//' /app/entrypoint.sh && exec /bin/sh /app/entrypoint.sh"]
```

**What this means:**

- When the container starts, run this command
- It fixes line endings again (in case bind mount overwrites the file) and runs entrypoint.sh

---

### 📜 What is entrypoint.sh and Why Do We Need It?

**The Problem:**
Your Django app needs PostgreSQL. But when docker-compose starts both containers, Django might start BEFORE PostgreSQL is ready. Django tries to connect → crash!

**The Solution: entrypoint.sh**
A script that runs BEFORE your main app, to check that everything is ready.

```bash
#!/bin/sh
```

**Line 1: The "shebang"**

- Tells Linux: "Use `/bin/sh` shell to run this script"
- Must be the FIRST line, no spaces before `#`

---

```bash
echo "Waiting for PostgreSQL..."
```

**Line 2: Just a log message**

- `echo` = print to screen
- Helps you debug by seeing what's happening

---

```bash
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
```

**Lines 3-5: The waiting loop**

Let's decode this:

| Part        | Meaning                                                 |
| ----------- | ------------------------------------------------------- |
| `while`     | Keep doing this...                                      |
| `!`         | ...as long as the next command FAILS                    |
| `nc -z`     | "netcat zero-I/O mode" - just check if port is open     |
| `$DB_HOST`  | Environment variable (will be `db` from docker-compose) |
| `$DB_PORT`  | Environment variable (will be `5432`)                   |
| `; do`      | Start the loop body                                     |
| `sleep 0.5` | Wait half a second                                      |
| `done`      | End of loop                                             |

**In plain English:**
"Keep checking if PostgreSQL's port is open. If not, wait 0.5 seconds and try again. Once it's open, continue."

**Visual timeline:**

```
Second 0: nc -z db 5432 → FAIL (PostgreSQL still starting)
Second 0.5: nc -z db 5432 → FAIL
Second 1: nc -z db 5432 → FAIL
Second 1.5: nc -z db 5432 → SUCCESS! Exit loop
```

---

```bash
echo "PostgreSQL is up - running migrations"
python manage.py migrate
```

**Lines 6-7: Run database migrations**

- Only runs after PostgreSQL is confirmed ready
- Creates/updates database tables

---

```bash
echo "Starting Django server"
exec python manage.py runserver 0.0.0.0:8000
```

**Lines 8-9: Start the Django server**

**Why `exec`?**
Without `exec`:

```
entrypoint.sh (PID 1)
└── python manage.py runserver (PID 2)
```

With `exec`:

```
python manage.py runserver (PID 1, REPLACES entrypoint.sh)
```

**Why does this matter?**

- Docker sends stop signals (SIGTERM) to PID 1
- Without `exec`, Django (PID 2) never receives the signal
- Container doesn't shut down gracefully

---

### 📦 Line-by-Line: Understanding docker-compose.yml

Your docker-compose.yml orchestrates multiple containers. Let's decode it:

```yaml
services:
```

**What this means:**

- "Here's a list of all the containers I want to run together"
- Each service = one container

---

```yaml
db:
  image: postgres:15
```

**What this means:**

- Service named `db` (other services can reach it at hostname `db`)
- Use the official PostgreSQL version 15 image from Docker Hub
- No `build:` because we're using a pre-made image, not building our own

---

```yaml
restart: unless-stopped
```

**Restart policies explained:**

| Policy           | Meaning                                    |
| ---------------- | ------------------------------------------ |
| `no`             | Never restart (default)                    |
| `always`         | Always restart, even if stopped manually   |
| `on-failure`     | Restart only if container exits with error |
| `unless-stopped` | Restart unless YOU explicitly stopped it   |

---

```yaml
env_file:
  - ./backend/.env
environment:
  POSTGRES_DB: ${POSTGRES_DB:-coredb2}
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-Postgres@1234}
```

**What this means:**

- `env_file`: Load variables from this file into the container
- `environment`: Set specific variables (can use values from env_file)
- `${VAR:-default}`: Use `$VAR` if set, otherwise use `default`

**The flow:**

```
.env file has: POSTGRES_DB=mydb
              ↓
environment: POSTGRES_DB: ${POSTGRES_DB:-coredb2}
              ↓
Result: POSTGRES_DB=mydb (from .env, not default)
```

---

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

**What this means:**

- Create a "named volume" called `postgres_data`
- Mount it to `/var/lib/postgresql/data` inside the container
- This is where PostgreSQL stores its data files

**Why is this critical?**

```
WITHOUT volume:
├── docker compose down
├── All your data is DELETED
└── Start fresh every time 😱

WITH volume:
├── docker compose down
├── Volume still exists on your computer
├── docker compose up
└── All your data is RESTORED 🎉
```

---

```yaml
healthcheck:
  test:
    [
      "CMD-SHELL",
      "pg_isready -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-coredb2}",
    ]
  interval: 10s
  timeout: 5s
  retries: 5
```

**What this means:**

| Part            | Meaning                                       |
| --------------- | --------------------------------------------- |
| `test:`         | Command to check if container is healthy      |
| `pg_isready`    | PostgreSQL's built-in "are you ready?" tool   |
| `interval: 10s` | Check every 10 seconds                        |
| `timeout: 5s`   | If check takes longer than 5s, it failed      |
| `retries: 5`    | After 5 failures, mark container as unhealthy |

**Why `$$` instead of `$`?**

- Single `$` in docker-compose = variable interpolation by Docker Compose
- Double `$$` = escape it, pass a literal `$` to the container
- Inside container, shell interprets `$POSTGRES_USER`

---

```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
```

**What this means:**

- Build an image from the Dockerfile in `./backend` folder
- `context:` = "where to look for files when COPY is used"

---

```yaml
volumes:
  - ./backend:/app
```

**This is a BIND MOUNT (different from named volume):**

| Feature    | Named Volume       | Bind Mount                |
| ---------- | ------------------ | ------------------------- |
| Syntax     | `volumename:/path` | `./hostpath:/path`        |
| Managed by | Docker             | You                       |
| Use case   | Database data      | Development (live reload) |

**Why use bind mount for backend?**

```
You edit views.py on your computer
        ↓
Bind mount syncs it to /app/views.py in container
        ↓
Django sees the change and reloads
        ↓
No rebuild needed! 🚀
```

---

```yaml
depends_on:
  db:
    condition: service_healthy
```

**What this means:**

- Don't start `backend` until `db` is healthy
- "healthy" = healthcheck passed
- Without this, Django might start before PostgreSQL is ready

**depends_on evolution:**

```yaml
# OLD way (just waits for container to START, not be READY)
depends_on:
  - db

# NEW way (waits for HEALTHCHECK to pass)
depends_on:
  db:
    condition: service_healthy
```

---

### 🔄 What Actually Happens When You Run `docker compose up --build`

Let me walk you through the EXACT sequence:

```
YOU TYPE: docker compose up --build
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Parse docker-compose.yml                        │
│ - Read all services, volumes, networks                  │
│ - Check for syntax errors                               │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Create network                                  │
│ "Creating network django_social_media_default"          │
│ - All services can now talk to each other by name       │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Create volumes                                  │
│ "Creating volume django_social_media_postgres_data"     │
│ - Allocates disk space for persistent data              │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Build backend image                             │
│ - Reads Dockerfile                                      │
│ - Downloads python:3.11-slim (if not cached)            │
│ - Runs each instruction (RUN, COPY, etc.)               │
│ - Tags result as "django_social_media-backend"          │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Start db container                              │
│ - Pull postgres:15 image (if not cached)                │
│ - Create container from image                           │
│ - Mount postgres_data volume                            │
│ - Set environment variables                             │
│ - Start PostgreSQL server                               │
│ - Run healthchecks every 10s                            │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Wait for db to be healthy                       │
│ Healthcheck: pg_isready -U postgres -d coredb2          │
│ - Attempt 1: FAIL (PostgreSQL still initializing)       │
│ - Attempt 2: FAIL                                       │
│ - Attempt 3: SUCCESS ✓                                  │
│ Container marked as "healthy"                           │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 7: Start backend container                         │
│ - Create container from built image                     │
│ - Mount ./backend to /app (bind mount)                  │
│ - Set environment variables (DB_HOST=db, etc.)          │
│ - Run ENTRYPOINT (which runs entrypoint.sh)             │
│                                                         │
│   entrypoint.sh:                                        │
│   1. While loop: nc -z db 5432 → SUCCESS (db is ready)  │
│   2. python manage.py migrate (create tables)           │
│   3. exec python manage.py runserver 0.0.0.0:8000       │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ DONE! Both services running                             │
│                                                         │
│ db:      PostgreSQL listening on port 5432              │
│ backend: Django listening on port 8000                  │
│                                                         │
│ You can now visit http://localhost:8000                 │
└─────────────────────────────────────────────────────────┘
```

---

### 🐛 Common Errors and What They Mean

#### Error: "exec ./entrypoint.sh: no such file or directory"

**You saw this one!**

**Cause:** Windows CRLF line endings in entrypoint.sh

```
What Windows writes: #!/bin/sh\r\n
What Linux sees:     #!/bin/sh\r     ← \r is part of "sh" now!
Linux looks for:     /bin/sh\r       ← doesn't exist!
```

**Fix:** Our Dockerfile now has `sed -i 's/\r$//'` to remove `\r`

---

#### Error: "The 'DB_NAME' variable is not set"

**Cause:** docker-compose.yml uses `${DB_NAME}` but no value was provided

**Fix:** Either:

1. Create `.env` file with `DB_NAME=mydb`
2. Or use defaults: `${DB_NAME:-mydb}`

---

#### Error: "Django requires Python 3.12+"

**You saw this one!**

**Cause:** Django 6+ requires Python 3.12, but Dockerfile uses Python 3.11

**Fix:** Either:

1. Change Dockerfile to `FROM python:3.12-slim`
2. Or use Django 5.x (what we did)

---

#### Error: "connection refused" to database

**Cause:** Django started before PostgreSQL was ready

**Fix:**

1. Add `healthcheck` to db service
2. Add `depends_on: db: condition: service_healthy` to backend
3. Use entrypoint.sh to wait for db port

---

### 🎯 Memory Tricks for Interviews

**Dockerfile instructions - "FROM WC RCE" (From Working Copy, Run Commands, Expose)**

- **F**ROM - base image
- **W**ORKDIR - cd to directory
- **C**OPY - copy files
- **R**UN - execute during build
- **C**MD - default command
- **E**NTRYPOINT - fixed command
- **E**XPOSE - document port

**docker run flags - "DIPE" (Dipe the container)**

- **D** = `-d` detached
- **I** = `-it` interactive terminal
- **P** = `-p` ports
- **E** = `-e` environment

**Volume types - "NBT" (like network broadcast)**

- **N**amed volume = `myvolume:/path` (Docker manages)
- **B**ind mount = `./local:/path` (you manage)
- **T**mpfs = in-memory (for secrets)

---

### 🧪 Practice Exercises

**Exercise 1: Build understanding**
Run this and explain each line of output:

```bash
docker build -t test-image .
```

**Exercise 2: See layers**

```bash
docker history django_social_media-backend
```

Each row = one instruction from Dockerfile

**Exercise 3: Enter a running container**

```bash
docker compose exec backend sh
# Now you're INSIDE the container!
ls -la
cat /app/manage.py
env | grep DB
exit
```

**Exercise 4: Watch logs in real-time**

```bash
docker compose logs -f backend
# Press Ctrl+C to stop watching
```

**Exercise 5: See what's happening**

```bash
docker compose ps              # Status of services
docker stats                   # Live CPU/memory usage
docker compose top             # Processes in containers
```

---

## Docker Commands Cheatsheet

### Image Commands

```bash
# List all images
docker images
docker image ls

# Pull an image from registry
docker pull <image>:<tag>
docker pull python:3.11-slim
docker pull postgres:15
docker pull redis:7-alpine

# Build image from Dockerfile
docker build -t <name>:<tag> .
docker build -t myapp:1.0 .
docker build -t myapp:latest -f Dockerfile.prod .

# Remove image
docker rmi <image>
docker image rm <image>

# Remove all unused images
docker image prune -a

# Tag an image
docker tag <source> <target>
docker tag myapp:1.0 myregistry/myapp:1.0

# Push to registry
docker push <image>:<tag>

# Inspect image
docker image inspect <image>

# Image history (see layers)
docker history <image>
```

### Container Commands

```bash
# Run a container
docker run <image>
docker run -d <image>                    # Detached (background)
docker run -it <image> bash              # Interactive with terminal
docker run -p 8000:8000 <image>          # Port mapping host:container
docker run -v /host/path:/container/path # Volume mount
docker run --name mycontainer <image>    # Named container
docker run --rm <image>                  # Remove after exit
docker run -e VAR=value <image>          # Environment variable
docker run --env-file .env <image>       # Load env from file

# Common run combinations
docker run -d -p 8000:8000 --name backend -e DEBUG=True myapp
docker run -it --rm python:3.11 python   # Quick Python REPL

# List containers
docker ps                                # Running only
docker ps -a                             # All (including stopped)
docker ps -q                             # Only IDs

# Stop container
docker stop <container>
docker stop $(docker ps -q)              # Stop all running

# Start stopped container
docker start <container>

# Restart container
docker restart <container>

# Remove container
docker rm <container>
docker rm -f <container>                 # Force remove running
docker rm $(docker ps -aq)               # Remove all

# Container logs
docker logs <container>
docker logs -f <container>               # Follow (live)
docker logs --tail 100 <container>       # Last 100 lines
docker logs --since 10m <container>      # Last 10 minutes

# Execute command in running container
docker exec <container> <command>
docker exec -it <container> bash         # Interactive shell
docker exec -it <container> sh           # For alpine images
docker exec mydb psql -U postgres        # Run psql in postgres container

# Copy files
docker cp <container>:/path /local/path  # From container
docker cp /local/path <container>:/path  # To container

# Container stats
docker stats                             # Live resource usage
docker top <container>                   # Running processes

# Inspect container
docker inspect <container>
docker inspect -f '{{.NetworkSettings.IPAddress}}' <container>
```

### System Commands

```bash
# System info
docker info
docker version

# Disk usage
docker system df

# Clean up everything
docker system prune              # Remove unused data
docker system prune -a           # Remove all unused (including images)
docker system prune --volumes    # Include volumes

# Events
docker events                    # Real-time events
```

### Network Commands

```bash
# List networks
docker network ls

# Create network
docker network create <name>
docker network create --driver bridge mynetwork

# Connect container to network
docker network connect <network> <container>

# Disconnect
docker network disconnect <network> <container>

# Inspect network
docker network inspect <network>

# Remove network
docker network rm <network>
```

### Volume Commands

```bash
# List volumes
docker volume ls

# Create volume
docker volume create <name>

# Inspect volume
docker volume inspect <name>

# Remove volume
docker volume rm <name>

# Remove unused volumes
docker volume prune
```

---

## Dockerfile Deep Dive

### Basic Structure

```dockerfile
# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="you@email.com"
LABEL version="1.0"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY . .

# Run commands during build
RUN pip install -r requirements.txt

# Expose port (documentation)
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Dockerfile Instructions

| Instruction   | Description                      | Example                    |
| ------------- | -------------------------------- | -------------------------- |
| `FROM`        | Base image                       | `FROM python:3.11-slim`    |
| `WORKDIR`     | Set working directory            | `WORKDIR /app`             |
| `COPY`        | Copy files from host             | `COPY . .`                 |
| `ADD`         | Copy + extract archives + URLs   | `ADD app.tar.gz /app`      |
| `RUN`         | Execute commands during build    | `RUN pip install django`   |
| `ENV`         | Set environment variables        | `ENV DEBUG=False`          |
| `ARG`         | Build-time variables             | `ARG VERSION=1.0`          |
| `EXPOSE`      | Document exposed port            | `EXPOSE 8000`              |
| `VOLUME`      | Create mount point               | `VOLUME /data`             |
| `USER`        | Set user for subsequent commands | `USER appuser`             |
| `CMD`         | Default command (overridable)    | `CMD ["python", "app.py"]` |
| `ENTRYPOINT`  | Fixed command (args appended)    | `ENTRYPOINT ["python"]`    |
| `HEALTHCHECK` | Container health check           | See below                  |

### ENTRYPOINT vs CMD

```dockerfile
# CMD - Default command, can be overridden
FROM python:3.11
CMD ["python", "app.py"]
# docker run myimage              → runs: python app.py
# docker run myimage python -V    → runs: python -V (overrides CMD)

# ENTRYPOINT - Fixed command, CMD provides default args
FROM python:3.11
ENTRYPOINT ["python"]
CMD ["app.py"]
# docker run myimage              → runs: python app.py
# docker run myimage other.py     → runs: python other.py

# Combined (best practice for scripts)
FROM python:3.11
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["runserver"]
```

### Multi-stage Builds

```dockerfile
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Best Practices

```dockerfile
# 1. Use specific tags, not :latest
FROM python:3.11.4-slim    # Good
FROM python:latest         # Bad

# 2. Minimize layers - combine RUN commands
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 3. Order from least to most frequently changing
COPY requirements.txt .          # Changes rarely
RUN pip install -r requirements.txt
COPY . .                         # Changes often

# 4. Use .dockerignore
# .dockerignore file:
# .git
# __pycache__
# *.pyc
# .env
# node_modules
# .venv

# 5. Don't run as root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# 6. Use HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
```

---

## Docker Compose

### Basic Structure

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=True

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Complete Reference

```yaml
services:
  backend:
    # Build from Dockerfile
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        - VERSION=1.0

    # Or use existing image
    image: python:3.11

    # Container name
    container_name: my-backend

    # Restart policy
    restart: unless-stopped  # no | always | on-failure | unless-stopped

    # Port mapping
    ports:
      - "8000:8000"          # host:container
      - "8001:8001"

    # Volume mounts
    volumes:
      - ./backend:/app                    # Bind mount
      - static_data:/app/static           # Named volume
      - /app/node_modules                 # Anonymous volume

    # Environment variables
    environment:
      - DEBUG=True
      - DB_HOST=db

    # Or from file
    env_file:
      - .env
      - .env.local

    # Dependencies
    depends_on:
      - db
      - redis

    # Or with health condition
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

    # Networks
    networks:
      - backend-network
      - frontend-network

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M

    # Command override
    command: python manage.py runserver 0.0.0.0:8000

    # Entrypoint override
    entrypoint: /app/entrypoint.sh

    # Working directory
    working_dir: /app

    # User
    user: "1000:1000"

networks:
  backend-network:
    driver: bridge
  frontend-network:

volumes:
  static_data:
  postgres_data:
    driver: local
```

### Compose Commands

```bash
# Start services
docker compose up
docker compose up -d                     # Detached
docker compose up --build                # Rebuild images
docker compose up -d --build             # Both

# Stop services
docker compose down
docker compose down -v                   # Remove volumes too
docker compose down --rmi all            # Remove images too

# Restart
docker compose restart
docker compose restart backend           # Specific service

# View logs
docker compose logs
docker compose logs -f                   # Follow
docker compose logs backend              # Specific service
docker compose logs --tail=100 backend

# List containers
docker compose ps

# Execute in container
docker compose exec backend bash
docker compose exec db psql -U postgres

# Run one-off command
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend pytest

# Build without cache
docker compose build --no-cache

# Pull latest images
docker compose pull

# View config
docker compose config                    # Validate and view

# Scale services
docker compose up -d --scale worker=3
```

---

## PostgreSQL in Docker

### Quick Start

```bash
# Run PostgreSQL container
docker run -d \
    --name postgres-db \
    -e POSTGRES_USER=admin \
    -e POSTGRES_PASSWORD=secretpassword \
    -e POSTGRES_DB=myappdb \
    -p 5432:5432 \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:15

# Connect to PostgreSQL
docker exec -it postgres-db psql -U admin -d myappdb
```

### Environment Variables

| Variable            | Description           | Default                    |
| ------------------- | --------------------- | -------------------------- |
| `POSTGRES_USER`     | Superuser username    | `postgres`                 |
| `POSTGRES_PASSWORD` | Superuser password    | (required)                 |
| `POSTGRES_DB`       | Default database name | Same as `POSTGRES_USER`    |
| `PGDATA`            | Data directory        | `/var/lib/postgresql/data` |

### Docker Compose Setup

```yaml
services:
  db:
    image: postgres:15
    container_name: postgres-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: myappdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql # Init script
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d myappdb"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Creating Database, User, Password

#### Method 1: Environment Variables (on first run)

```yaml
environment:
  POSTGRES_USER: myuser
  POSTGRES_PASSWORD: mypassword
  POSTGRES_DB: mydatabase
```

#### Method 2: Init Script

Create `init.sql`:

```sql
-- Create additional users
CREATE USER app_user WITH PASSWORD 'app_password';
CREATE USER readonly_user WITH PASSWORD 'readonly_password';

-- Create additional databases
CREATE DATABASE production_db;
CREATE DATABASE staging_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE production_db TO app_user;
GRANT CONNECT ON DATABASE production_db TO readonly_user;

-- Create tables
\c production_db;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL
);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

Mount it:

```yaml
volumes:
  - ./init.sql:/docker-entrypoint-initdb.d/init.sql
```

#### Method 3: Inside Running Container

```bash
# Connect as superuser
docker exec -it postgres-db psql -U admin

# Inside psql:
CREATE USER newuser WITH PASSWORD 'newpassword';
CREATE DATABASE newdb OWNER newuser;
GRANT ALL PRIVILEGES ON DATABASE newdb TO newuser;
\q
```

### Changing Password

#### Method 1: Using psql

```bash
# Connect to container
docker exec -it postgres-db psql -U admin

# Change password
ALTER USER admin WITH PASSWORD 'newpassword';
ALTER USER myuser WITH PASSWORD 'anothernewpassword';
\q
```

#### Method 2: Using SQL file

```bash
docker exec -it postgres-db psql -U admin -c "ALTER USER admin WITH PASSWORD 'newpassword';"
```

#### Method 3: Recreate Container (for superuser)

```bash
# Stop and remove (keep volume!)
docker stop postgres-db
docker rm postgres-db

# Run with new password
docker run -d \
    --name postgres-db \
    -e POSTGRES_USER=admin \
    -e POSTGRES_PASSWORD=NEWPASSWORD \
    -e POSTGRES_DB=myappdb \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:15
```

> ⚠️ Note: POSTGRES_PASSWORD only sets password on first initialization. After that, change via ALTER USER.

### Common PostgreSQL Commands in Docker

```bash
# Connect to database
docker exec -it postgres-db psql -U admin -d myappdb

# List databases
docker exec -it postgres-db psql -U admin -c "\l"

# List users
docker exec -it postgres-db psql -U admin -c "\du"

# List tables
docker exec -it postgres-db psql -U admin -d myappdb -c "\dt"

# Describe table
docker exec -it postgres-db psql -U admin -d myappdb -c "\d users"

# Run SQL file
docker exec -i postgres-db psql -U admin -d myappdb < script.sql

# Backup database
docker exec -t postgres-db pg_dump -U admin myappdb > backup.sql
docker exec -t postgres-db pg_dumpall -U admin > all_databases.sql

# Restore database
docker exec -i postgres-db psql -U admin -d myappdb < backup.sql

# Create database
docker exec -it postgres-db createdb -U admin newdatabase

# Drop database
docker exec -it postgres-db dropdb -U admin olddatabase
```

### PostgreSQL with Django

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    environment:
      DB_HOST: db
      DB_PORT: 5432
    depends_on:
      db:
        condition: service_healthy
```

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}
```

---

## Redis in Docker

### What is Redis?

Redis is an in-memory data structure store used as:

- **Cache** - Speed up database queries
- **Message Broker** - For Celery task queues
- **Session Store** - Store user sessions
- **Pub/Sub** - Real-time messaging

### Quick Start

```bash
# Run Redis
docker run -d \
    --name redis \
    -p 6379:6379 \
    redis:7-alpine

# With password
docker run -d \
    --name redis \
    -p 6379:6379 \
    redis:7-alpine \
    redis-server --requirepass mypassword

# With persistence
docker run -d \
    --name redis \
    -p 6379:6379 \
    -v redis_data:/data \
    redis:7-alpine \
    redis-server --appendonly yes

# Connect to Redis CLI
docker exec -it redis redis-cli
docker exec -it redis redis-cli -a mypassword  # With password
```

### Docker Compose Setup

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass mypassword
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "mypassword", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

### Redis Commands Reference

#### Connection & Server

```bash
# Connect
redis-cli
redis-cli -h hostname -p 6379 -a password

# Inside redis-cli
PING                    # Returns PONG if connected
AUTH password           # Authenticate
SELECT 0                # Select database (0-15)
INFO                    # Server info
DBSIZE                  # Number of keys
FLUSHDB                 # Clear current database
FLUSHALL                # Clear all databases
SHUTDOWN                # Stop server
```

#### String Operations

```bash
# Set and Get
SET key "value"
GET key
SET user:1:name "John"
GET user:1:name

# Set with expiration
SET session:abc123 "data" EX 3600    # Expires in 3600 seconds
SETEX key 60 "value"                  # Same as above

# Multiple operations
MSET key1 "val1" key2 "val2"
MGET key1 key2

# Increment/Decrement
SET counter 10
INCR counter               # 11
INCRBY counter 5           # 16
DECR counter               # 15

# Check existence
EXISTS key
SETNX key "value"          # Set if Not eXists
```

#### Key Operations

```bash
KEYS *                     # All keys (avoid in production!)
KEYS user:*                # Pattern match
SCAN 0 MATCH user:* COUNT 100  # Safe iteration

DEL key                    # Delete key
EXPIRE key 60              # Set TTL in seconds
TTL key                    # Time to live (-1 = no expiry, -2 = doesn't exist)
PERSIST key                # Remove expiration
RENAME key newkey
TYPE key                   # Get data type
```

#### List Operations (Queues)

```bash
# Add to list
LPUSH mylist "first"       # Add to left (head)
RPUSH mylist "last"        # Add to right (tail)

# Get from list
LPOP mylist                # Remove from left
RPOP mylist                # Remove from right
LRANGE mylist 0 -1         # Get all elements
LLEN mylist                # List length
LINDEX mylist 0            # Get by index

# Blocking pop (for queues)
BLPOP queue 30             # Block 30 seconds waiting for element
BRPOP queue 30
```

#### Set Operations

```bash
SADD myset "member1" "member2"
SMEMBERS myset             # All members
SISMEMBER myset "member1"  # Check membership
SREM myset "member1"       # Remove member
SCARD myset                # Count members

# Set operations
SUNION set1 set2           # Union
SINTER set1 set2           # Intersection
SDIFF set1 set2            # Difference
```

#### Hash Operations (Objects)

```bash
# Store object
HSET user:1 name "John" age 30 email "john@example.com"

# Get fields
HGET user:1 name
HMGET user:1 name age
HGETALL user:1

# Other operations
HDEL user:1 email
HEXISTS user:1 name
HKEYS user:1
HVALS user:1
HINCRBY user:1 age 1
```

#### Sorted Sets (Leaderboards)

```bash
ZADD leaderboard 100 "player1" 200 "player2" 150 "player3"
ZRANGE leaderboard 0 -1              # By rank (low to high)
ZREVRANGE leaderboard 0 -1           # By rank (high to low)
ZRANK leaderboard "player1"          # Get rank
ZSCORE leaderboard "player1"         # Get score
ZRANGEBYSCORE leaderboard 100 200    # By score range
```

#### Pub/Sub

```bash
# Subscriber (Terminal 1)
SUBSCRIBE channel1

# Publisher (Terminal 2)
PUBLISH channel1 "Hello!"

# Pattern subscribe
PSUBSCRIBE news.*
```

### Redis with Django

#### Installation

```bash
pip install django-redis redis
```

#### Cache Backend

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "mypassword",
        }
    }
}

# Usage
from django.core.cache import cache

cache.set("key", "value", timeout=300)  # 5 minutes
value = cache.get("key")
cache.delete("key")
```

#### Session Backend

```python
# settings.py
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

#### Celery Broker

```python
# settings.py
CELERY_BROKER_URL = "redis://:mypassword@redis:6379/1"
CELERY_RESULT_BACKEND = "redis://:mypassword@redis:6379/2"
```

### Redis Best Practices

1. **Always set TTL** on cache keys
2. **Use namespaced keys**: `app:user:123:profile`
3. **Avoid KEYS command** in production - use SCAN
4. **Enable persistence** for important data
5. **Set maxmemory policy** to handle memory limits

---

## React App in Docker

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

EXPOSE 3000

# Start dev server
CMD ["npm", "start"]
```

### Production Dockerfile (Multi-stage)

```dockerfile
# Dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Config for React Router

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy (optional)
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose for React

```yaml
# Development
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules    # Prevent overwriting node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
      - CHOKIDAR_USEPOLLING=true  # Hot reload on Windows

# Production
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

### React + Django + PostgreSQL + Redis

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DB_HOST=db
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redispassword
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "redispassword", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

---

## Django + Postgres + Redis Stack

### Complete Production Setup

```yaml
# docker-compose.yml
services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - backend

  # Django backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    expose:
      - "8000"
    env_file:
      - ./backend/.env
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://:redispass@redis:6379/0
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

  # Celery worker
  celery:
    build: ./backend
    env_file:
      - ./backend/.env
    environment:
      - DB_HOST=db
      - REDIS_URL=redis://:redispass@redis:6379/0
    depends_on:
      - backend
      - redis
    command: celery -A config worker -l info

  # Celery beat (scheduler)
  celery-beat:
    build: ./backend
    env_file:
      - ./backend/.env
    environment:
      - REDIS_URL=redis://:redispass@redis:6379/0
    depends_on:
      - backend
      - redis
    command: celery -A config beat -l info

  # PostgreSQL
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: proddb
      POSTGRES_USER: produser
      POSTGRES_PASSWORD: prodpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U produser -d proddb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redispass --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "redispass", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

---

## Networking

### Network Types

| Type      | Description                       | Use Case                    |
| --------- | --------------------------------- | --------------------------- |
| `bridge`  | Default. Isolated network on host | Single-host multi-container |
| `host`    | Use host's network directly       | Maximum performance         |
| `none`    | No networking                     | Security/isolation          |
| `overlay` | Multi-host networking             | Docker Swarm                |

### Container Communication

```yaml
# Containers in same compose network can reach each other by service name
services:
  backend:
    # Can reach db at "db:5432" and redis at "redis:6379"
    depends_on:
      - db
      - redis

  db:
    image: postgres:15

  redis:
    image: redis:7
```

### Custom Networks

```yaml
services:
  frontend:
    networks:
      - frontend-net

  backend:
    networks:
      - frontend-net
      - backend-net

  db:
    networks:
      - backend-net

networks:
  frontend-net:
  backend-net:
```

### Network Commands

```bash
# Create
docker network create mynetwork

# Run container in network
docker run --network mynetwork --name app1 myimage

# Connect existing container
docker network connect mynetwork existing-container

# Inspect
docker network inspect mynetwork

# List containers in network
docker network inspect mynetwork -f '{{range .Containers}}{{.Name}} {{end}}'
```

---

## Volumes & Data Persistence

### Volume Types

| Type         | Syntax               | Use Case                  |
| ------------ | -------------------- | ------------------------- |
| Named Volume | `myvolume:/data`     | Persistent data (DB)      |
| Bind Mount   | `./local:/container` | Development, config files |
| Anonymous    | `/data`              | Temporary, auto-removed   |
| tmpfs        | `tmpfs: /tmp`        | Security, performance     |

### Examples

```yaml
services:
  app:
    volumes:
      # Named volume (managed by Docker)
      - app_data:/app/data

      # Bind mount (host path)
      - ./config:/app/config:ro # Read-only
      - ./uploads:/app/uploads

      # Anonymous volume (preserve node_modules during bind mount)
      - /app/node_modules

      # tmpfs (in-memory)
    tmpfs:
      - /tmp

volumes:
  app_data:
    driver: local
```

### Backup & Restore Volumes

```bash
# Backup
docker run --rm \
    -v postgres_data:/data \
    -v $(pwd):/backup \
    alpine tar cvf /backup/postgres_backup.tar /data

# Restore
docker run --rm \
    -v postgres_data:/data \
    -v $(pwd):/backup \
    alpine tar xvf /backup/postgres_backup.tar -C /
```

---

## Interview Questions & Answers

### Basic Questions

**Q: What is Docker?**

> Docker is a containerization platform that packages applications with their dependencies into standardized units called containers. Unlike VMs, containers share the host OS kernel, making them lightweight and fast.

**Q: Difference between Docker image and container?**

> An **image** is a read-only template (like a class). A **container** is a running instance of an image (like an object). You can run multiple containers from one image.

**Q: What is a Dockerfile?**

> A text file containing instructions to build a Docker image. Each instruction creates a layer in the image.

**Q: CMD vs ENTRYPOINT?**

> - **CMD**: Default command, can be overridden at runtime
> - **ENTRYPOINT**: Fixed command, arguments are appended
> - Best practice: Use ENTRYPOINT for the command, CMD for default arguments

**Q: COPY vs ADD?**

> - **COPY**: Simply copies files from host to container
> - **ADD**: Also handles URLs and auto-extracts archives
> - Best practice: Use COPY unless you need ADD's extra features

### Intermediate Questions

**Q: How do containers communicate?**

> Containers on the same Docker network can communicate using container names as hostnames. Docker Compose automatically creates a network for all services.

**Q: What are Docker volumes?**

> Volumes provide persistent storage that survives container restarts. Types:
>
> - **Named volumes**: Managed by Docker, portable
> - **Bind mounts**: Maps host directory, good for development
> - **tmpfs**: In-memory, for sensitive data

**Q: How to reduce Docker image size?**

> 1. Use slim/alpine base images
> 2. Multi-stage builds
> 3. Combine RUN commands to reduce layers
> 4. Use .dockerignore
> 5. Remove cache after installing packages

**Q: What is Docker Compose?**

> A tool for defining and running multi-container applications using a YAML file. It handles networking, volumes, environment variables, and service dependencies.

**Q: Explain multi-stage builds**

> Multi-stage builds use multiple FROM statements to create intermediate images. Only the final stage is kept, reducing image size by excluding build tools and dependencies.

### Advanced Questions

**Q: How does Docker networking work?**

> - **bridge**: Default. Creates isolated network with NAT
> - **host**: Shares host network, no isolation
> - **overlay**: For multi-host (Swarm)
> - **none**: Disables networking

**Q: What is the Docker build cache?**

> Docker caches each layer of an image. If a layer's instruction and context haven't changed, it reuses the cached layer. Order Dockerfile instructions from least to most frequently changing for optimal caching.

**Q: How to handle secrets in Docker?**

> 1. Environment variables (not ideal, visible in inspect)
> 2. Docker secrets (Swarm only)
> 3. .env files (not in image)
> 4. External secret managers (Vault, AWS Secrets Manager)
> 5. BuildKit secrets for build-time secrets

**Q: Container vs VM - when to use which?**

> - **Containers**: Microservices, stateless apps, rapid scaling, CI/CD
> - **VMs**: Different OS required, strong isolation needed, legacy apps

**Q: Explain Docker's copy-on-write mechanism**

> Containers share the read-only image layers. When a container writes to a file, Docker copies that file to the container's writable layer first. This makes container creation fast and storage efficient.

**Q: How to debug a crashed container?**

```bash
# View logs
docker logs container_name

# Check exit code
docker inspect container_name --format='{{.State.ExitCode}}'

# Run with shell to debug
docker run -it --entrypoint sh image_name

# Inspect filesystem of stopped container
docker commit stopped_container debug_image
docker run -it debug_image sh
```

**Q: Healthcheck best practices?**

> - Check application-specific endpoints (/health)
> - Set appropriate intervals (10-30s)
> - Use realistic timeouts
> - Define start_period for slow-starting apps
> - Make healthcheck commands lightweight

### Scenario-Based Questions

**Q: Your container keeps restarting. How do you debug?**

> 1. `docker logs container_name` - Check for errors
> 2. `docker inspect container_name` - Check exit code and state
> 3. Run interactively: `docker run -it image_name sh`
> 4. Check resource limits, healthcheck settings
> 5. Verify entry point script for errors

**Q: How would you deploy a Django app with PostgreSQL?**

> Use Docker Compose with:
>
> 1. PostgreSQL service with named volume
> 2. Django service with depends_on and health check
> 3. Proper environment variables
> 4. Network for container communication
> 5. Entry point script for migrations

**Q: How to optimize a Node.js Dockerfile?**

```dockerfile
# Use specific slim image
FROM node:18-alpine

WORKDIR /app

# Install deps first (cached layer)
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Non-root user
USER node

CMD ["node", "app.js"]
```

---

## Quick Reference Card

### Must-Know Commands

```bash
# Build & Run
docker build -t app .
docker run -d -p 8000:8000 --name app -e ENV=prod app

# Logs & Debug
docker logs -f app
docker exec -it app sh

# Compose
docker compose up -d --build
docker compose down -v
docker compose logs -f service

# Cleanup
docker system prune -a --volumes
```

### Must-Know Compose

```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment: [DEBUG=False]
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./app:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
```

### Must-Know Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
```

---

_Last updated: March 2026_
