# CWSO Local Docker Desktop Deployment Guide

**Version:** 1.0
**Last updated:** 2026-06-28
**Environment:** Docker Desktop (Mac, Windows, Linux)
**Minimum requirements:** Docker 20.10+, 4GB RAM, 2GB disk space

---

## Quick Start (5 minutes)

```bash
# 1. Clone or navigate to emage.code
cd ~/Code/emage/emage.code

# 2. Run the automated setup
bash scripts/deploy/cwso-docker-desktop.sh

# 3. Verify it's running
curl http://localhost:8080/health

# Done! CWSO is now running locally
```

---

## Detailed Setup

### Prerequisites

- **Docker Desktop installed** — [Download here](https://www.docker.com/products/docker-desktop)
- **Docker running** — Start Docker Desktop application
- **bash or zsh shell** — For running setup scripts
- **4GB minimum RAM allocated to Docker** — Check Docker preferences
- **Ports 8080, 8787 available** — Default CWSO ports

### Step 1: Prepare Environment

```bash
# Navigate to repository
cd ~/Code/emage/emage.code

# Create deployment directory
mkdir -p deploy/local-dev

# Copy configuration
cp deploy/docker-compose-local-dev.yml deploy/local-dev/docker-compose.yml
cp deploy/docker-compose-local-dev.env deploy/local-dev/.env
```

### Step 2: Configure JWT Secret

```bash
# Option A: Use provided development JWT (for testing only)
cd deploy/local-dev
source ../.env.jwt.dev
echo "JWT_SECRET=$JWT_SECRET" >> .env

# Option B: Generate new JWT for your instance
cd deploy/local-dev
export JWT_SECRET=$(head -c 32 /dev/urandom | base64)
echo "JWT_SECRET=$JWT_SECRET" >> .env
```

**⚠️ Important:**
- The `.env.jwt.dev` JWT is **for development only**
- Never use development JWTs in production
- Store JWT secrets securely (use env vars, vault, or secrets management)

### Step 3: Start CWSO Stack

```bash
cd deploy/local-dev

# Start all containers
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Expected output:
# NAME                COMMAND              STATUS
# cwso-orchestrator   "python3 ..."        Up 2 seconds
# cwso-rollout       "python3 ..."        Up 2 seconds
# cwso-git-shadow    "python3 ..."        Up 2 seconds
# cwso-merge-engine  "python3 ..."        Up 2 seconds
```

### Step 4: Verify Deployment

```bash
# Check orchestrator health
curl http://localhost:8080/health

# Expected response:
# {"status":"healthy","timestamp":"2026-06-28T08:45:00Z"}

# Check rollout proxy
curl http://localhost:8787/health

# Test JWT authentication
JWT_SECRET=$(grep JWT_SECRET deploy/local-dev/.env | cut -d= -f2)
TOKEN=$(python3 -c "
import jwt
import json
secret = '$JWT_SECRET'
payload = {'sub': 'test-user', 'role': 'admin'}
token = jwt.encode(payload, secret, algorithm='HS256')
print(token)
")

curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/status
```

---

## Common Tasks

### Viewing Logs

```bash
cd deploy/local-dev

# View all logs (follow mode)
docker-compose logs -f

# View specific service
docker-compose logs -f orchestrator

# View last 50 lines
docker-compose logs --tail=50 rollout-proxy
```

### Stopping CWSO

```bash
cd deploy/local-dev

# Stop all containers (data preserved)
docker-compose stop

# Restart containers
docker-compose start
```

### Removing CWSO (Clean Slate)

```bash
cd deploy/local-dev

# Stop and remove containers
docker-compose down

# Remove volumes (⚠️ deletes all data)
docker-compose down -v
```

### Updating CWSO Image

```bash
cd deploy/local-dev

# Pull latest images
docker-compose pull

# Recreate containers with latest images
docker-compose up -d --force-recreate

# Or via convenience script
bash ../../scripts/deploy/cwso-docker-desktop.sh --update
```

### Testing with Sample Requests

```bash
cd deploy/local-dev

# Generate JWT token
JWT_SECRET=$(grep JWT_SECRET .env | cut -d= -f2)
TOKEN=$(python3 -c "
import jwt
secret = '$JWT_SECRET'
payload = {'sub': 'test-agent', 'role': 'executor'}
print(jwt.encode(payload, secret, algorithm='HS256'))
")

# Sample dispatch request
curl -X POST http://localhost:8080/dispatch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_role": "backend-developer",
    "task_id": "T001",
    "objective": "Test dispatch",
    "context": "Local Docker test"
  }'
```

---

## Troubleshooting

### Port Already in Use

**Problem:** `Port 8080 is already allocated`

**Solutions:**
```bash
# Option 1: Find and stop the process using the port
lsof -i :8080
kill -9 <PID>

# Option 2: Use different ports
# Edit deploy/local-dev/docker-compose.yml
# Change ports: "8080:8080" to "8081:8080"
# Then rebuild

# Option 3: Check if CWSO is already running
docker-compose ps
```

### Out of Memory

**Problem:** `OOMKilled` or containers crash with memory errors

**Solutions:**
1. Increase Docker memory allocation:
   - Mac/Windows: Docker Desktop → Preferences → Resources → Memory → increase to 6-8GB
   - Linux: Increase available memory or reduce container limits in docker-compose.yml

2. Reduce container resource limits:
```yaml
# In docker-compose.yml
services:
  orchestrator:
    mem_limit: 1024m  # Reduce from default 2G
    mem_reservation: 512m
```

### JWT Authentication Failed

**Problem:** `401 Unauthorized` or `Invalid token` errors

**Solutions:**
```bash
# 1. Verify JWT is in environment
grep JWT_SECRET deploy/local-dev/.env

# 2. Verify JWT matches in requests
TOKEN=$(python3 -c "import jwt; print(jwt.encode({'sub': 'test'}, '$(grep JWT_SECRET .env | cut -d= -f2)', algorithm='HS256'))")
echo "Token: $TOKEN"

# 3. Check logs for token validation errors
docker-compose logs orchestrator | grep -i "token\|auth"

# 4. Regenerate JWT if corrupted
rm deploy/local-dev/.env
cp deploy/docker-compose-local-dev.env deploy/local-dev/.env
source ../../deploy/.env.jwt.dev
echo "JWT_SECRET=$JWT_SECRET" >> deploy/local-dev/.env
docker-compose restart
```

### Network Connection Issues

**Problem:** `Connection refused` or `Cannot connect to localhost:8080`

**Solutions:**
```bash
# 1. Verify containers are running
docker-compose ps

# 2. Check network configuration
docker network ls
docker network inspect <cwso-network>

# 3. Inspect container networking
docker inspect cwso-orchestrator | grep -A 10 NetworkSettings

# 4. Test from inside container
docker-compose exec orchestrator curl http://localhost:8080/health

# 5. Restart containers
docker-compose restart
```

### Containers Won't Start

**Problem:** `docker-compose up` fails with errors

**Solutions:**
```bash
# 1. Check logs for errors
docker-compose logs

# 2. Verify images exist
docker images | grep cwso

# 3. Pull images explicitly
docker-compose pull

# 4. Rebuild images
docker-compose build --no-cache

# 5. Check configuration
docker-compose config | grep -A 5 orchestrator

# 6. Full reset
docker-compose down -v
docker system prune
docker-compose pull
docker-compose up -d
```

---

## Performance Tuning

### For Development (Default)
```yaml
# docker-compose.yml defaults
orchestrator:
  mem_limit: 2g
  cpus: 1.0
rollout-proxy:
  mem_limit: 1g
  cpus: 0.5
```

Adequate for:
- Single-developer workstations
- Testing and validation
- PoC deployments

### For Higher Load Testing
```yaml
orchestrator:
  mem_limit: 4g
  cpus: 2.0
rollout-proxy:
  mem_limit: 2g
  cpus: 1.0
```

Increase Docker memory allocation to 8GB before applying these settings.

---

## Monitoring and Healthchecks

### Built-in Health Checks

```bash
# Check orchestrator health
curl http://localhost:8080/health

# Check rollout proxy health
curl http://localhost:8787/health

# Check all services
for port in 8080 8787 8788 8789; do
  echo "Port $port:"
  curl -s http://localhost:$port/health | jq '.' || echo "  [not responding]"
done
```

### Container Status

```bash
# Continuous monitoring
docker stats cwso-orchestrator cwso-rollout-proxy

# Memory usage over time
docker-compose exec orchestrator free -h

# Disk usage
docker system df
```

### Logs Analysis

```bash
# View logs with timestamps
docker-compose logs --timestamps

# Search for errors
docker-compose logs | grep -i error

# Stream specific service logs
docker-compose logs -f orchestrator --tail 20
```

---

## Data Persistence

### Parquet Store
The Parquet trajectory store is created at `/tmp/t226-parquet-store` by default.

```bash
# Backup trajectory data
cp -r /tmp/t226-parquet-store ~/backup/cwso-trajectories-$(date +%Y%m%d)

# Verify backup
ls -lah ~/backup/cwso-trajectories-*
```

### Volume Management

```bash
# List Docker volumes
docker volume ls | grep cwso

# Inspect volume
docker volume inspect cwso-local-dev_orchestrator-data

# Backup volume data
docker run --rm -v cwso-local-dev_orchestrator-data:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data

# Restore volume from backup
docker run --rm -v cwso-local-dev_orchestrator-data:/data -v $(pwd):/backup alpine tar xzf /backup/volume-backup.tar.gz -C /
```

---

## Backup and Restore

### Full Backup

```bash
# Create backup directory
mkdir -p ~/backups/cwso-local
BACKUP_DIR=~/backups/cwso-local/cwso-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR

# Backup volumes
docker volume inspect cwso-local-dev_orchestrator-data 2>/dev/null && \
  docker run --rm -v cwso-local-dev_orchestrator-data:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/volumes.tar.gz /data

# Backup configuration
cp -r deploy/local-dev $BACKUP_DIR/config

# Backup trajectories
cp -r /tmp/t226-parquet-store $BACKUP_DIR/trajectories 2>/dev/null || true

echo "Backup complete: $BACKUP_DIR"
```

### Restore from Backup

```bash
# Identify backup to restore
ls -la ~/backups/cwso-local/

BACKUP_DIR=~/backups/cwso-local/cwso-backup-<timestamp>

# Stop CWSO
cd deploy/local-dev
docker-compose down -v

# Restore volumes
docker volume create cwso-local-dev_orchestrator-data
docker run --rm -v cwso-local-dev_orchestrator-data:/data -v $BACKUP_DIR:/backup \
  alpine tar xzf /backup/volumes.tar.gz -C /

# Restore configuration (if needed)
cp $BACKUP_DIR/config/.env .env

# Restore trajectories
mkdir -p /tmp/t226-parquet-store
cp -r $BACKUP_DIR/trajectories/* /tmp/t226-parquet-store/ 2>/dev/null || true

# Restart CWSO
docker-compose up -d

echo "Restore complete"
```

---

## Next Steps

### After Successful Deployment
1. ✅ Verify all health checks pass
2. ✅ Test sample dispatch requests
3. ✅ Review logs for any warnings
4. ✅ Set up monitoring (if needed)
5. ✅ Proceed to production deployment when ready

### For Production Deployment
- See [Proxmox LXC Deployment Guide](proxmox-lxc-guide.md) for on-premises
- See [GCP Cloud Run Deployment Guide](gcp-cloud-run-guide.md) for cloud

### For Support
- Review the troubleshooting section above
- See [Deployment Troubleshooting Guide](troubleshooting-guide.md)
- Check deployment logs
- Consult the main README

---

## Support and Questions

For issues or questions:
1. Check the troubleshooting section above
2. See [Deployment Troubleshooting Guide](troubleshooting-guide.md)
3. Review deployment logs: `docker-compose logs`
4. Consult the main README: `/home/emage/Code/emage/emage.code/README.md`
5. Check CWSO documentation: `/home/emage/Code/emage/CWSO/README.md`

---

## Appendix: Docker Compose Configuration

See `docker-compose-local-dev.yml` and `docker-compose-local-dev.env` in the `deploy/` directory for full configuration details.

Key services:
- **orchestrator** (port 8080) — Main CWSO orchestration engine
- **rollout-proxy** (port 8787) — Model routing and request proxying
- **git-shadow** (port 8788) — Git shadowing service
- **merge-engine** (port 8789) — Concurrent merge engine
