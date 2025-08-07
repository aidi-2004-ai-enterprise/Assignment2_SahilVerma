# Docker Deployment Guide

This document provides comprehensive instructions for deploying the Penguin Species Classification API using Docker with **GCP-hosted model loading**.

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
```powershell
docker build -t ml-pipeline-app:latest .
```

### Running the Container
```powershell
# Run with GCP models (recommended)
docker run -p 8080:8080 `
  -v "D:\AI DEV\CICD_bipin\Assignment2_SahilVerma\gcp\sa-key.json:/gcp/sa-key.json:ro" `
  -e GCS_BUCKET_NAME=my-penguin-api-bucket `
  ml-pipeline-app:latest

# Run with local models (fallback)
docker run -p 8080:8080 -e GCS_BUCKET_NAME= ml-pipeline-app:latest
```

### Resource Monitoring
```bash
# Monitor CPU/memory usage
docker stats
```

### Image Inspection
```bash
# Inspect image layers and size
docker inspect ml-pipeline-app:latest
```

## Docker Image Analysis Results

### Image Size and Layers
- **Total Size**: 816.7 MB (816,746,950 bytes)
- **Layers**: 13 layers total
- **Architecture**: linux/amd64
- **Base Image**: python:3.10-slim

### Key Features
- **User**: Non-root user 'app' for security
- **Exposed Port**: 8080/tcp
- **Working Directory**: /app
- **Health Check**: Configured with 30s interval, 10s timeout
- **Environment Variables**: Production-optimized Python settings

## Testing with Service Account

## 🚀 Running Locally

### Option 1: Local Docker with GCP Models (Recommended)
```powershell
# Build the image
docker build -t ml-pipeline-app:latest .

# Run with GCP-hosted models (allows model updates without rebuilding)
docker run -p 8080:8080 `
  -v "D:\AI DEV\CICD_bipin\Assignment2_SahilVerma\gcp\sa-key.json:/gcp/sa-key.json:ro" `
  -e GOOGLE_APPLICATION_CREDENTIALS=/gcp/sa-key.json `
  -e GCS_BUCKET_NAME=my-penguin-api-bucket `
  ml-pipeline-app:latest

# Run in background
docker run -d -p 8080:8080 --name ml-gcp `
  -v "D:\path\to\your-service-account-key.json:/gcp/sa-key.json:ro" `
  -e GCS_BUCKET_NAME=your-penguin-api-bucket `
  ml-pipeline-app:latest

# View logs
docker logs ml-gcp

# Stop container
docker stop ml-gcp && docker rm ml-gcp
```

### Option 2: Local Docker with Local Models (Fallback)
```powershell
# Override GCP config to use local model files
docker run -p 8080:8080 -e GCS_BUCKET_NAME= ml-pipeline-app:latest
```

### Option 3: Local Development Environment
```powershell
# Install dependencies
uv sync

# Set up environment (create .env file with GCP config)
echo 'GCS_BUCKET_NAME=your-penguin-api-bucket' > .env
echo 'GCS_MODEL_PATH=model.json' >> .env
echo 'GCS_METADATA_PATH=model_metadata.json' >> .env
echo 'GOOGLE_APPLICATION_CREDENTIALS=D:\path\to\your-service-account-key.json' >> .env

# Run locally
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Volume-mount Service Account Key (GCP Testing)

**Security Note**: The `.env` file is excluded from Docker images (in `.dockerignore`) and Git commits (in `.gitignore`) for security. All configuration is passed via environment variables at runtime.

**Step 1: Run container with environment variables**
```bash
# No need to rebuild - configuration is passed at runtime
docker build -t ml-pipeline-app:latest .
```

**Step 2: Run with volume-mounted service account**
```powershell
# All configuration passed via environment variables (secure approach)
docker run -d -p 8080:8080 --name ml-pipeline-gcp-test `
  -v "D:\path\to\your-service-account-key.json:/gcp/sa-key.json:ro" `
  -e GOOGLE_APPLICATION_CREDENTIALS=/gcp/sa-key.json `
  -e GCS_BUCKET_NAME=my-penguin-api-bucket `
  -e GCS_MODEL_PATH=model.json `
  -e GCS_METADATA_PATH=model_metadata.json `
  ml-pipeline-app:latest

# Check logs to verify GCS connection
docker logs ml-pipeline-gcp-test
```

**Volume Mount Explanation:**
- `host_path`: Absolute path to service account key on your local machine  
- `container_path`: `/gcp/sa-key.json` - where the key appears in the container
- `options`: `:ro` means read-only for security
- Environment variables override .env values for testing

**✅ Working Container Test (Local Model)**
If you want to test the container functionality without GCP:
```powershell
# Override GCP config to use local model files
docker run -d -p 8080:8080 --name ml-pipeline-local -e GCS_BUCKET_NAME= ml-pipeline-app:latest

# Test the API (PowerShell)
$body = @{
    bill_length_mm = 39.1
    bill_depth_mm = 18.7
    flipper_length_mm = 181
    body_mass_g = 3750
    year = 2007
    sex = "male"
    island = "Torgersen"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/predict" -Method POST -Body $body -ContentType "application/json"
# Expected: {"predicted_species":"Adelie","confidence":0.9987375140190125}
```

### Test Endpoints
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8080/" -Method GET
# Expected: {"status":"healthy","model_loaded":true}

# Alternative with curl (if available)
curl http://localhost:8080/

# Prediction test with curl
curl -X POST "http://localhost:8080/predict" `
  -H "Content-Type: application/json" `
  -d '{\"bill_length_mm\": 39.1, \"bill_depth_mm\": 18.7, \"flipper_length_mm\": 181, \"body_mass_g\": 3750, \"year\": 2007, \"sex\": \"male\", \"island\": \"Torgersen\"}'
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
- **GCP Integration**: Supports Google Cloud Storage for model loading

### GCP Service Account Setup

For Cloud Run deployment with GCP model storage:

1. **Create/Use Service Account** with Storage Object Viewer permissions
2. **Set Environment Variables** at deployment time (no credentials in image)
3. **Use IAM-based authentication** instead of credential files

### Environment Variables for GCP

```bash
# For local development (with service account key)
GOOGLE_APPLICATION_CREDENTIALS=/GCP/sa-key.json

# For Cloud Run (uses default service account)
# No GOOGLE_APPLICATION_CREDENTIALS needed - uses metadata service
```

## ☁️ Google Cloud Run Deployment

### Prerequisites
```bash
# Install gcloud CLI and authenticate
gcloud auth login
gcloud config set project YOUR-PROJECT-ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Method 1: Using Cloud Build (Simplest)
```powershell
# Build and deploy in one command
gcloud builds submit --tag us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest

# Deploy to Cloud Run
gcloud run deploy ml-pipeline-service `
  --image us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest `
  --platform managed `
  --region us-east1 `
  --allow-unauthenticated `
  --port 8080 `
  --memory 1Gi `
  --cpu 1 `
  --set-env-vars GCS_BUCKET_NAME=your-penguin-api-bucket
```

### Method 2: Manual Push to Artifact Registry

#### Step 1: Create Artifact Registry Repository
```powershell
gcloud artifacts repositories create ml-pipeline-repo `
  --repository-format=docker `
  --location=us-east1 `
  --description="ML Pipeline Docker images"
```

#### Step 2: Configure Docker Authentication
```powershell
gcloud auth configure-docker us-east1-docker.pkg.dev
```

#### Step 3: Build and Push Image
```powershell
# Build locally
docker build -t ml-pipeline-app:latest .

# Tag for Artifact Registry
docker tag ml-pipeline-app:latest `
  us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest

# Push to registry
docker push us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest
```

#### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy ml-pipeline-service \
  --image us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1
```

### Service Account Setup (if using GCS)
```bash
# Create service account for Cloud Run
gcloud iam service-accounts create cloud-run-ml-service \
  --display-name="Cloud Run ML Service Account"

# Grant access to GCS bucket
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:cloud-run-ml-service@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Deploy with service account
gcloud run deploy ml-pipeline-service \
  --image us-east1-docker.pkg.dev/YOUR-PROJECT-ID/ml-pipeline-repo/ml-pipeline-app:latest \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --service-account cloud-run-ml-service@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

## 🧪 Testing Your Deployment

### Local Docker Testing
```bash
# Start container
docker run -d -p 8080:8080 --name ml-test ml-pipeline-app:latest

# Wait a few seconds for startup, then test
sleep 5

# Health check
curl http://localhost:8080/
# Expected: {"status":"healthy"}

# Prediction test
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
# Expected: {"predicted_species":"Adelie","confidence":0.95}

# Monitor resources
docker stats ml-test --no-stream

# Clean up
docker stop ml-test && docker rm ml-test
```

### Cloud Run Testing
```bash
# After deployment, get the service URL
gcloud run services describe ml-pipeline-service \
  --region us-east1 \
  --format 'value(status.url)'

# Test health endpoint
curl https://YOUR-SERVICE-URL/

# Test prediction endpoint
curl -X POST "https://YOUR-SERVICE-URL/predict" \
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

## 📊 Performance Monitoring

### Resource Usage
```bash
# Monitor local container
docker stats ml-test

# Check Cloud Run metrics
gcloud monitoring dashboards list
```

### Typical Resource Usage
- **Memory**: ~100MB (with model loaded)
- **CPU**: <1% (idle), ~10% (during predictions)
- **Cold Start**: ~2-3 seconds
- **Response Time**: <100ms per prediction

## 🔍 Troubleshooting

### Common Issues
- key issues
- Service account issues


#### 1. Container Won't Start


```bash
# Check logs
docker logs CONTAINER_ID

# Common fix: Rebuild image
docker build -t ml-pipeline-app:latest .
```

#### 2. Model Loading Errors
- Ensure `app/data/model.json` exists in the image
- Check `.env` configuration for GCS settings
- Verify GCP service account permissions

#### 3. GCP Authentication Issues
```bash
# Check current project
gcloud config get-value project

# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

#### 4. Network/Timeout Issues
- Use Cloud Build instead of local push
- Check firewall settings
- Verify region settings match

## ✅ Verification Checklist

## Endpoint : 
https://ml-pipeline-service-217500056249.us-east1.run.app/docs

### Local Deployment
- [ ] Container builds without errors
- [ ] Health endpoint returns 200
- [ ] Prediction endpoint works
- [ ] Model loads successfully
- [ ] Resource usage is reasonable

### GCP Deployment  
- [ ] Image pushes to Artifact Registry : Done 
- [ ] Cloud Run service deploys : Done 
- [ ] Service is publicly accessible : Done 
- [ ] Authentication works (if needed) : None
- [ ] Monitoring is configured : 

### Production Readiness
- [ ] Security best practices implemented
- [ ] Health checks configured
- [ ] Logging is functional
- [ ] Error handling works
- [ ] Performance is acceptable

The containerized application is production-ready and can be deployed on Google Cloud Run or any Docker-compatible platform.