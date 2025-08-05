# Docker Deployment Guide

This document provides comprehensive instructions for deploying the Penguin Species Classification API using Docker.

## Overview

The application is containerized using Docker for production deployment, optimized for performance and security. The container is designed to run on Google Cloud Run with port 8080.

## Files Created

### 1. `Dockerfile`
- **Base Image**: `python:3.10-slim` for minimal footprint
- **Security**: Non-root user (`app`) for enhanced security
- **Optimization**: Multi-stage dependency installation with layer caching
- **Health Check**: Built-in health monitoring using curl
- **Port**: Exposes port 8080 for Cloud Run compatibility

### 2. `requirements.txt`
Production-ready dependencies excluding development packages:
- Core runtime dependencies (FastAPI, Uvicorn, Pydantic)
- ML dependencies (XGBoost, scikit-learn, pandas, numpy)
- Visualization libraries (matplotlib, seaborn)
- Supporting libraries for data handling

### 3. `.dockerignore`
Excludes unnecessary files to reduce build context:
- Python cache files (`__pycache__/`, `*.pyc`)
- Test files and coverage reports
- Development tools (`.git/`, `.vscode/`, `.idea/`)
- Environment files (`.env`, `.venv/`)
- OS-specific files

## Build and Run Commands

### Building the Image
```bash
docker build -t penguin-classifier .
```

### Running the Container
```bash
# Run in detached mode
docker run -d -p 8080:8080 --name penguin-api penguin-classifier

# Run with logs visible
docker run -p 8080:8080 --name penguin-api penguin-classifier
```

### Testing the API
```bash
# Test the prediction endpoint
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "bill_length_mm": 39.1,
    "bill_depth_mm": 18.7,
    "flipper_length_mm": 181,
    "body_mass_g": 3750,
    "year": 2007,
    "sex": "male",
    "island": "Torgersen"
  }'
```

Expected response:
```json
{"predicted_species":"Adelie","confidence":0.9987375140190125}
```

## Resource Monitoring

### Check Container Stats
```bash
docker stats penguin-api --no-stream
```

### Typical Resource Usage
- **CPU**: ~0.22% (idle state)
- **Memory**: ~100MB (with model loaded)
- **Processes**: ~34 PIDs
- **Network**: Minimal I/O during idle

## Image Analysis

### Image Inspection
```bash
docker inspect penguin-classifier
```

### Image Details from Analysis

**Size**: 2.58GB
- Large size due to ML dependencies (XGBoost, scikit-learn, matplotlib)
- NVIDIA CUDA libraries included with XGBoost (~322MB)

**Layers**: 13 layers total
- Base python:3.10-slim layers
- System dependency installation
- Python package installation (largest layer)
- Application code and model data
- Security and configuration layers

**Architecture**: linux/amd64

**Key Configuration**:
- Working Directory: `/app`
- User: `app` (non-root)
- Exposed Port: `8080/tcp`
- Health Check: Every 30s with 10s timeout
- Environment Variables: Production optimized

## Security Features

1. **Non-root User**: Container runs as user `app` for security
2. **Minimal Base Image**: Uses `python:3.10-slim` to reduce attack surface
3. **Health Checks**: Built-in monitoring for container health
4. **Environment Variables**: Production-optimized Python settings
5. **Clean Package Installation**: No cache retention to reduce size

## Performance Optimizations

1. **Layer Caching**: Requirements copied first for better build caching
2. **No Cache Installs**: `--no-cache-dir` prevents disk bloat
3. **Build Dependencies**: Cleaned after package installation
4. **Single Worker**: Configured for Cloud Run's single-instance model
5. **Optimized Environment**: Python bytecode writing disabled

## Issues Encountered and Solutions

### 1. Large Image Size (2.58GB)
**Issue**: ML dependencies significantly increase image size
**Solution**: 
- Used slim base image instead of full Python image
- Removed build dependencies after installation
- Excluded development packages from requirements.txt

### 2. Health Check Configuration
**Issue**: Initial health check used Python requests library
**Solution**: 
- Switched to curl for lightweight health checking
- Adjusted health check intervals for Cloud Run compatibility

### 3. Permission Issues
**Issue**: Security requirements for production deployment
**Solution**: 
- Created non-root user `app`
- Proper file ownership with `chown`
- Switched to non-root user before CMD

### 4. Dependency Management
**Issue**: Balancing required packages vs. image size
**Solution**: 
- Carefully curated requirements.txt excluding dev dependencies
- Kept visualization libraries as they may be used by model dependencies

## Cloud Run Deployment Notes

The container is specifically configured for Google Cloud Run:
- **Port 8080**: Hard-coded as required by Cloud Run
- **Single Worker**: Optimized for Cloud Run's instance model
- **Health Checks**: Compatible with Cloud Run health monitoring
- **Non-root User**: Meets Cloud Run security requirements
- **Environment Variables**: Production-ready configuration

## Verification Results

✅ **Container builds without errors**
✅ **Endpoints match non-containerized app behavior**
✅ **Proper resource utilization** (100MB RAM, <1% CPU)
✅ **Security best practices** implemented
✅ **Health checks** functional
✅ **Port 8080** exposed and accessible

The containerized application is ready for production deployment on Google Cloud Run or any Docker-compatible platform.