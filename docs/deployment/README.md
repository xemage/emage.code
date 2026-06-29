# CWSO Deployment Guides

Complete documentation for deploying CWSO (Orchestration & SIA Infrastructure) across multiple hosting environments.

---

## Choose Your Deployment Environment

### 🖥️ Local Development — Docker Desktop
**Best for:** Developers, testing, rapid prototyping  
**Setup time:** 5 minutes  
**Requirements:** Docker Desktop, 4GB RAM  
**Cost:** Free (on your machine)

[📖 Docker Desktop Deployment Guide →](local-docker-desktop-guide.md)

**Quick start:**
```bash
bash scripts/deploy/cwso-docker-desktop.sh
curl http://localhost:8080/health
```

---

### 🏢 On-Premises Lab — Proxmox LXC
**Best for:** Lab environments, staging, local infrastructure  
**Setup time:** 15 minutes  
**Requirements:** Proxmox VE 7.0+, 4GB RAM per container  
**Cost:** Infrastructure-dependent

[📖 Proxmox LXC Deployment Guide →](proxmox-lxc-guide.md)

**Quick start:**
```bash
scp scripts/deploy/cwso-proxmox-setup.sh root@proxmox-host:/tmp/
ssh root@proxmox-host "bash /tmp/cwso-proxmox-setup.sh --auto"
```

---

### ☁️ Cloud — Google Cloud Run
**Best for:** Production, high availability, auto-scaling  
**Setup time:** 20 minutes  
**Requirements:** GCP account with billing  
**Cost:** $0.40 per million invocations + compute

[📖 GCP Cloud Run Deployment Guide →](gcp-cloud-run-guide.md)

**Quick start:**
```bash
docker build -t gcr.io/$PROJECT_ID/cwso:latest .
docker push gcr.io/$PROJECT_ID/cwso:latest
gcloud run deploy cwso-orchestrator \
  --image gcr.io/$PROJECT_ID/cwso:latest \
  --platform managed --region us-central1
```

---

## Deployment Comparison

| Feature | Docker Desktop | Proxmox | GCP Cloud Run |
|---------|---|---|---|
| **Setup Time** | 5 min | 15 min | 20 min |
| **Cost** | Free | Infrastructure | $$$$ |
| **Scalability** | Single machine | Vertical | Automatic |
| **Persistence** | Volumes | Storage pools | Cloud Storage |
| **Monitoring** | Docker stats | Proxmox | Cloud Logging |
| **Best For** | Development | Staging/Lab | Production |
| **Difficulty** | ⭐ Easy | ⭐⭐ Moderate | ⭐⭐ Moderate |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│    CWSO Components (same everywhere)            │
├─────────────────────────────────────────────────┤
│  - Orchestrator service (8080)                  │
│  - Rollout proxy (8787)                         │
│  - Git shadow (8788)                            │
│  - Merge engine (8789)                          │
│  - Parquet trajectory store                     │
│  - JWT authentication                           │
│  - Health monitoring                            │
└─────────────────────────────────────────────────┘
        ↓               ↓              ↓
    ┌────────┐    ┌──────────┐   ┌──────────┐
    │ Docker │    │ Proxmox  │   │ GCP      │
    │Desktop │    │ LXC      │   │ Cloud Run│
    └────────┘    └──────────┘   └──────────┘
```

---

## Pre-Deployment Checklist

### All Environments
- [ ] Repository cloned: `git clone https://gitlab.com/em-age/emage.code.git`
- [ ] Dependencies installed (Docker/gcloud as needed)
- [ ] Internet connectivity verified
- [ ] Sufficient disk space available (minimum 10GB)
- [ ] Adequate memory allocated (4GB minimum)

### Docker Desktop Only
- [ ] Docker Desktop installed and running
- [ ] Ports 8080, 8787, 8788, 8789 available
- [ ] 4GB RAM allocated in Docker preferences

### Proxmox Only
- [ ] SSH access to Proxmox host
- [ ] Ubuntu 20.04 template available
- [ ] Network bridge configured (vmbr0 typical)
- [ ] Container ID range decided (200-299 typical)

### GCP Only
- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] GCP project created
- [ ] Cloud Run API enabled

---

## Common Deployment Tasks

### Health Check

```bash
# Docker Desktop
curl http://localhost:8080/health

# Proxmox (from container or host)
ssh 192.168.1.100 "curl http://localhost:8080/health"

# GCP
curl $(gcloud run services describe cwso-orchestrator \
  --platform managed --region us-central1 \
  --format='value(status.url)')/health
```

### View Logs

```bash
# Docker Desktop
cd deploy/local-dev && docker-compose logs -f

# Proxmox
pct enter 201 "docker-compose logs -f"

# GCP
gcloud logging read "resource.type=cloud_run_revision" --limit 50 --follow
```

### Stop Deployment

```bash
# Docker Desktop
cd deploy/local-dev && docker-compose down

# Proxmox
pct stop 201

# GCP
gcloud run services delete cwso-orchestrator --region us-central1
```

### Backup Data

```bash
# Docker Desktop
docker volume inspect cwso-local-dev_orchestrator-data

# Proxmox
vzdump 201 --dumpdir /var/backups/cwso

# GCP
gsutil -m cp -r gs://project-cwso-parquet/* ~/backups/cwso/
```

---

## Troubleshooting Quick Reference

### Service Won't Start

1. **Docker Desktop**: `docker-compose logs` → check for port conflicts
2. **Proxmox**: `pct logs 201` → verify network configuration
3. **GCP**: `gcloud run operations list` → check deployment errors

### Can't Access Service

1. **Docker Desktop**: `curl http://localhost:8080/health`
2. **Proxmox**: `ping 192.168.1.100` → verify network
3. **GCP**: Check firewall rules, verify service URL

### Authentication Failed

1. Check JWT secret: `grep JWT_SECRET .env`
2. Verify token in request headers
3. Check logs for token validation errors

### Storage Issues

1. **Docker Desktop**: `docker system df` → check volume space
2. **Proxmox**: `df -h` inside container → check disk
3. **GCP**: `gsutil du gs://bucket-name` → check storage usage

See individual deployment guides for detailed troubleshooting sections.

---

## Monitoring and Operations

### Essential Metrics
- Response time (latency)
- Error rate
- Request throughput
- Resource utilization (CPU, memory, disk)
- Parquet trajectory count

### Health Endpoints
```bash
# Orchestrator
GET /health

# Rollout Proxy
GET /health

# Status endpoints
GET /api/status
```

### Alerting
- Error rate > 5%
- Response time P95 > 500ms
- Disk usage > 80%
- Memory usage > 90%

---

## Migration Between Environments

### From Docker Desktop to Proxmox

```bash
# 1. Backup Docker volumes
docker run --rm -v cwso-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/volume.tar.gz /data

# 2. Transfer backup to Proxmox
scp volume.tar.gz root@proxmox-host:/tmp/

# 3. Deploy to Proxmox
bash /tmp/cwso-proxmox-setup.sh --restore /tmp/volume.tar.gz
```

### From Proxmox to GCP

```bash
# 1. Backup container
vzdump 201 --dumpdir /tmp

# 2. Extract Parquet data
scp -r root@proxmox-host:/var/lib/cwso/parquet ./

# 3. Upload to GCP
gsutil -m cp -r parquet/* gs://project-cwso-parquet/

# 4. Deploy to GCP
bash scripts/deploy/cwso-gcp-deploy.sh --restore-data
```

---

## Security Considerations

### JWT Secrets
- **Never commit secrets** to version control
- Store in `.env.local` (gitignored)
- Use Secret Manager in production (GCP)
- Rotate secrets regularly

### Network Access
- **Docker Desktop**: Localhost only (secure)
- **Proxmox**: Firewall rules + network segmentation
- **GCP**: Identity-Aware Proxy (IAP) + VPC

### Data Protection
- **Encryption at rest**: Enable in production
- **Encryption in transit**: Use HTTPS
- **Backup strategy**: Off-site copies
- **Access control**: IAM roles, RBAC

---

## Performance Optimization

### Scaling Strategies

**Docker Desktop** (limited):
- Vertical scaling: Increase RAM/CPU in Docker preferences
- Single-machine limitation

**Proxmox** (moderate):
- Horizontal: Add more containers
- Vertical: Increase container resources
- Load balancing: Use HAProxy

**GCP** (unlimited):
- Automatic horizontal scaling
- Auto-scaling based on CPU/memory
- Global load distribution

### Caching and Storage

- **Parquet store**: Optimize query patterns
- **Docker volumes**: Use named volumes
- **GCP Storage**: Enable CDN/caching
- **Database**: Connection pooling, indexing

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Documentation complete
- [ ] Security review completed
- [ ] Backup procedure tested
- [ ] Disaster recovery plan documented

### Deployment
- [ ] Infrastructure provisioned
- [ ] Configuration validated
- [ ] Secrets secured
- [ ] Monitoring enabled
- [ ] Team trained

### Post-Deployment
- [ ] Health checks passing
- [ ] Logs reviewed for errors
- [ ] Monitoring alerts active
- [ ] Documentation updated
- [ ] Runbook prepared for ops team

---

## Cost Optimization

### Docker Desktop
- **Cost**: Free (on personal hardware)
- **Optimization**: N/A

### Proxmox
- **Cost**: Infrastructure-dependent
- **Optimization**: Right-size resources, consolidate workloads

### GCP Cloud Run
- **Cost**: Per-invocation + compute
- **Optimization**: 
  - Increase min-instances cautiously
  - Use Cloud CDN for static content
  - Archive old data to Cloud Archive Storage
  - Set budget alerts

---

## Next Steps

### Choose Your Environment
1. **For development**: [Docker Desktop Guide](local-docker-desktop-guide.md)
2. **For staging**: [Proxmox LXC Guide](proxmox-lxc-guide.md)
3. **For production**: [GCP Cloud Run Guide](gcp-cloud-run-guide.md)

### Deploy Now
- Follow the deployment guide for your chosen environment
- Verify health endpoints
- Set up monitoring
- Test backup/restore procedure

### Continue Learning
- Review the individual deployment guide for your environment
- Check deployment logs for any issues
- Consult the main repository README

---

## Support and Resources

### Documentation
- Individual deployment guides (see sections above)
- Deployment scripts and configuration (in `scripts/deploy/`)

### External Resources
- [Docker Documentation](https://docs.docker.com)
- [Proxmox Documentation](https://pve.proxmox.com/wiki)
- [Google Cloud Docs](https://cloud.google.com/docs)

### Getting Help
1. Review the specific deployment guide for your environment
2. Check service logs
3. Search [emage.code Issues](https://gitlab.com/em-age/emage.code/-/issues)
4. Create new issue or contact team

---

## Contributing

Have feedback on these guides? Found errors or confusing sections?

1. Open an issue: https://gitlab.com/em-age/emage.code/-/issues
2. Submit MR with improvements
3. Contact deployment team

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-28 | Initial release: Docker Desktop, Proxmox, GCP |

---

**Last updated:** 2026-06-28  
**Maintainer:** DevOps Team  
**Next review:** 2026-09-28
