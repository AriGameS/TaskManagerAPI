# Docker Configuration Guide

## Overview

This project includes enhanced Docker configuration with multi-stage builds, health checks, and production optimizations for the TaskManagerAPI.

## Docker Files

### 1. **Dockerfile** - Multi-stage Production Build

**Features:**
- **Multi-stage build** for smaller, more secure images
- **Non-root user** for security
- **Health checks** for container monitoring
- **Production optimizations** with Gunicorn
- **Security hardening** with minimal dependencies

**Stages:**
1. **Builder Stage**: Installs dependencies and builds the application
2. **Production Stage**: Creates a minimal runtime image

### 2. **docker-compose.yml** - Production Configuration

**Features:**
- Production-ready configuration
- Health checks
- Resource limits
- Logging configuration
- Network isolation

### 3. **docker-compose.dev.yml** - Development Configuration

**Features:**
- Development environment
- Volume mounting for live code changes
- Optional database and Redis services
- Debug mode enabled

### 4. **docker-compose.prod.yml** - Full Production Stack

**Features:**
- Load balancer with Traefik
- SSL/TLS termination
- Monitoring with Prometheus and Grafana
- High availability configuration
- Resource management

## Usage

### Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Start with database
docker-compose -f docker-compose.dev.yml --profile database up

# Start with cache
docker-compose -f docker-compose.dev.yml --profile cache up

# Start with both database and cache
docker-compose -f docker-compose.dev.yml --profile database --profile cache up
```

### Production

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Start with monitoring
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Start with load balancer
docker-compose -f docker-compose.prod.yml --profile loadbalancer up -d

# Start full stack
docker-compose -f docker-compose.prod.yml --profile monitoring --profile loadbalancer up -d
```

### Building Images

```bash
# Build production image
docker build -t task-manager-api:latest .

# Build development image
docker build --target builder -t task-manager-api:dev .

# Build with specific platform
docker build --platform linux/amd64 -t task-manager-api:latest .
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Debug mode | `0` |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |
| `PYTHONDONTWRITEBYTECODE` | Python bytecode generation | `1` |

### Health Checks

The container includes health checks that:
- Check the `/health` endpoint every 30 seconds
- Timeout after 10 seconds
- Retry 3 times before marking as unhealthy
- Wait 5 seconds before starting checks

### Resource Limits

**Production Limits:**
- Memory: 512MB limit, 256MB reservation
- CPU: 0.5 cores limit, 0.25 cores reservation

**Development:**
- No resource limits (for development flexibility)

## Security Features

### 1. **Non-root User**
- Application runs as `appuser` instead of root
- Reduces security attack surface

### 2. **Minimal Dependencies**
- Only runtime dependencies in production image
- Build dependencies removed after build

### 3. **Multi-stage Build**
- Smaller image size
- No build tools in production image
- Reduced attack surface

### 4. **Health Checks**
- Container health monitoring
- Automatic restart on failure
- Load balancer health awareness

## Monitoring

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:
- Request count and duration
- Error rates
- System metrics
- Custom application metrics

### Grafana Dashboards

Pre-configured dashboards for:
- Application performance
- System metrics
- Error tracking
- Request patterns

### Access URLs

- **Application**: http://localhost:5125
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Traefik Dashboard**: http://localhost:8080

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if port is in use
   lsof -i :5125
   
   # Use different port
   docker run -p 5126:5125 task-manager-api:latest
   ```

2. **Permission Issues**
   ```bash
   # Fix log directory permissions
   sudo chown -R $USER:$USER logs/
   ```

3. **Health Check Failures**
   ```bash
   # Check container logs
   docker logs <container_id>
   
   # Check health status
   docker inspect <container_id> | grep Health -A 10
   ```

### Debug Mode

```bash
# Run in debug mode
docker run -e FLASK_DEBUG=1 -p 5125:5125 task-manager-api:latest

# Access container shell
docker exec -it <container_id> /bin/bash
```

## Performance Optimization

### 1. **Image Size**
- Multi-stage build reduces final image size
- Minimal base image (python:3.11-slim)
- No unnecessary packages

### 2. **Startup Time**
- Pre-built virtual environment
- Optimized layer caching
- Minimal runtime dependencies

### 3. **Runtime Performance**
- Gunicorn with multiple workers
- Connection pooling
- Request limits and timeouts

## Best Practices

### 1. **Image Building**
- Use specific version tags
- Build for target platform
- Use .dockerignore to exclude unnecessary files

### 2. **Security**
- Run as non-root user
- Use minimal base images
- Regular security updates
- Scan images for vulnerabilities

### 3. **Monitoring**
- Enable health checks
- Monitor resource usage
- Set up alerting
- Regular log rotation

### 4. **Deployment**
- Use orchestration tools (Docker Swarm, Kubernetes)
- Implement rolling updates
- Set up backup strategies
- Monitor deployment health

## Integration with CI/CD

The Docker configuration integrates with our GitHub Actions workflows:

- **Build**: Multi-stage builds in CI pipeline
- **Test**: Container testing in integration tests
- **Deploy**: Production deployment with health checks
- **Monitor**: Health check validation

## Next Steps

1. **Database Integration**: Add PostgreSQL or MongoDB
2. **Caching**: Implement Redis for session storage
3. **Load Balancing**: Configure multiple replicas
4. **SSL/TLS**: Set up certificate management
5. **Backup**: Implement data backup strategies
