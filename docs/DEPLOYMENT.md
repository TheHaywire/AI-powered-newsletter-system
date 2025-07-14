# AI Newsletter System - Deployment Guide

## Overview

This guide covers deploying the AI Newsletter Generator system in various environments, from local development to production cloud deployment.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Security Best Practices](#security-best-practices)
7. [Scaling Strategies](#scaling-strategies)

## Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BlogWriter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP models**
   ```bash
   python -c "import spacy; spacy.cli.download('en_core_web_sm')"
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Run setup script**
   ```bash
   python setup.py
   ```

7. **Test the system**
   ```bash
   python main.py --demo
   ```

## Docker Deployment

### Dockerfile

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p output archive logs data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for web interface
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "src/web_interface.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  newsletter-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEWS_API_KEY=${NEWS_API_KEY}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SENDER_EMAIL=${SENDER_EMAIL}
      - SENDER_PASSWORD=${SENDER_PASSWORD}
    volumes:
      - ./output:/app/output
      - ./archive:/app/archive
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=newsletter
      - POSTGRES_USER=newsletter_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - newsletter-app
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream newsletter_app {
        server newsletter-app:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://newsletter_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            alias /app/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Deployment Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f newsletter-app

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d --build
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECR repository**
   ```bash
   aws ecr create-repository --repository-name ai-newsletter
   ```

2. **Build and push Docker image**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t ai-newsletter .
   docker tag ai-newsletter:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-newsletter:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-newsletter:latest
   ```

3. **Create ECS cluster and service**
   ```bash
   # Create cluster
   aws ecs create-cluster --cluster-name newsletter-cluster

   # Create task definition
   aws ecs register-task-definition --cli-input-json file://task-definition.json

   # Create service
   aws ecs create-service --cluster newsletter-cluster --service-name newsletter-service --task-definition newsletter-task:1 --desired-count 2
   ```

#### Using AWS Lambda (Serverless)

```yaml
# serverless.yml
service: ai-newsletter

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    NEWS_API_KEY: ${env:NEWS_API_KEY}

functions:
  generate-newsletter:
    handler: handler.generate_newsletter
    events:
      - schedule: cron(0 9 ? * FRI *)  # Every Friday at 9 AM
      - http:
          path: /generate
          method: post

  web-interface:
    handler: handler.web_interface
    events:
      - http:
          path: /{proxy+}
          method: any
```

### Google Cloud Platform

#### Using Google Cloud Run

1. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/ai-newsletter
   gcloud run deploy ai-newsletter --image gcr.io/PROJECT_ID/ai-newsletter --platform managed
   ```

2. **Set environment variables**
   ```bash
   gcloud run services update ai-newsletter --set-env-vars OPENAI_API_KEY=your-key
   ```

#### Using Google Cloud Functions

```python
# main.py
import functions_framework
from newsletter_orchestrator import NewsletterOrchestrator

@functions_framework.http
def generate_newsletter(request):
    orchestrator = NewsletterOrchestrator()
    report = orchestrator.generate_newsletter()
    return {'success': True, 'report': report}
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image ai-newsletter .

# Deploy to Container Instances
az container create \
  --resource-group myResourceGroup \
  --name ai-newsletter \
  --image myregistry.azurecr.io/ai-newsletter:latest \
  --dns-name-label ai-newsletter \
  --ports 5000
```

## Production Considerations

### Environment Variables

```bash
# Required for production
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_news_api_key
SECRET_KEY=your_secret_key_here

# Email configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# Database configuration
DATABASE_URL=postgresql://user:password@localhost/newsletter

# Redis configuration
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

### Database Setup

```sql
-- PostgreSQL schema
CREATE TABLE subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    subscribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sent TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    preferences JSONB
);

CREATE TABLE newsletters (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    theme VARCHAR(255),
    word_count INTEGER,
    reading_time INTEGER
);

CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER REFERENCES subscribers(id),
    newsletter_id INTEGER REFERENCES newsletters(id),
    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT
);

CREATE INDEX idx_subscribers_email ON subscribers(email);
CREATE INDEX idx_newsletters_date ON newsletters(generated_date);
CREATE INDEX idx_email_logs_date ON email_logs(sent_date);
```

### Logging Configuration

```python
# logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
```

## Monitoring and Maintenance

### Health Checks

```python
# health_check.py
import requests
import psutil
import os

def check_system_health():
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check disk space
    disk_usage = psutil.disk_usage('/')
    if disk_usage.percent > 90:
        health_status['status'] = 'warning'
        health_status['checks']['disk_space'] = f"Disk usage: {disk_usage.percent}%"
    
    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        health_status['status'] = 'warning'
        health_status['checks']['memory'] = f"Memory usage: {memory.percent}%"
    
    # Check API connectivity
    try:
        response = requests.get('https://api.openai.com/v1/models', timeout=5)
        health_status['checks']['openai_api'] = 'connected'
    except:
        health_status['status'] = 'error'
        health_status['checks']['openai_api'] = 'disconnected'
    
    return health_status
```

### Metrics Collection

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
NEWSLETTER_GENERATED = Counter('newsletter_generated_total', 'Total newsletters generated')
GENERATION_DURATION = Histogram('newsletter_generation_duration_seconds', 'Newsletter generation time')
ACTIVE_SUBSCRIBERS = Gauge('active_subscribers', 'Number of active subscribers')
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['api_name'])

def track_generation_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        GENERATION_DURATION.observe(duration)
        NEWSLETTER_GENERATED.inc()
        return result
    return wrapper
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz output/ archive/ logs/

# Upload to cloud storage
aws s3 cp backup_*.sql s3://my-backup-bucket/
aws s3 cp backup_*.tar.gz s3://my-backup-bucket/

# Clean up old backups (keep last 7 days)
find . -name "backup_*.sql" -mtime +7 -delete
find . -name "backup_*.tar.gz" -mtime +7 -delete
```

## Security Best Practices

### API Key Management

```python
# key_management.py
import os
import base64
from cryptography.fernet import Fernet

class KeyManager:
    def __init__(self):
        self.cipher_suite = Fernet(os.getenv('ENCRYPTION_KEY').encode())
    
    def encrypt_key(self, api_key):
        return self.cipher_suite.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key):
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
```

### Input Validation

```python
# validation.py
import re
from typing import Optional

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_url(url: str) -> Optional[str]:
    if not url.startswith(('http://', 'https://')):
        return None
    return url

def validate_config(config: dict) -> bool:
    required_fields = ['newsletter_theme', 'quality_thresholds']
    return all(field in config for field in required_fields)
```

### Rate Limiting

```python
# rate_limiter.py
import time
from collections import defaultdict
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, key):
        now = time.time()
        self.requests[key] = [req for req in self.requests[key] 
                            if now - req < self.time_window]
        
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        return False

def rate_limit(max_requests=100, time_window=3600):
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed('default'):
                raise Exception("Rate limit exceeded")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Scaling Strategies

### Horizontal Scaling

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-newsletter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-newsletter
  template:
    metadata:
      labels:
        app: ai-newsletter
    spec:
      containers:
      - name: newsletter-app
        image: ai-newsletter:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Caching Strategy

```python
# cache_manager.py
import redis
import json
import hashlib
from typing import Any, Optional

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))
    
    def get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis_client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration"""
        self.redis_client.setex(key, expire, json.dumps(value))
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

### Load Balancing

```nginx
# nginx-load-balancer.conf
upstream newsletter_backend {
    least_conn;  # Least connections algorithm
    server backend1:5000 max_fails=3 fail_timeout=30s;
    server backend2:5000 max_fails=3 fail_timeout=30s;
    server backend3:5000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://newsletter_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

This deployment guide provides comprehensive instructions for deploying the AI Newsletter System in various environments, from local development to production cloud deployment, with considerations for security, monitoring, and scaling. 