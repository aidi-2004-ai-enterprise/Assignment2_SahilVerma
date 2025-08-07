# GitHub Actions CI/CD Pipeline

This repository includes comprehensive GitHub Actions workflows for automated testing, building, and deployment of the ML Pipeline application.

## 🚀 Workflows Overview

### 1. CI/CD Pipeline (`ci-cd.yml`)
**Triggers**: Push to `main/develop`, Pull Requests to `main`

**Jobs**:
- **Test**: Runs unit tests with coverage reporting
- **Lint**: Code quality checks with ruff and black
- **Build**: Docker image build with multi-platform support
- **Deploy**: Automated deployment to Cloud Run (main branch only)
- **Load Test**: Performance testing after deployment

### 2. PR Validation (`pr-validation.yml`)
**Triggers**: Pull Requests to `main/develop`

**Jobs**:
- **Security Scan**: Vulnerability scanning with Trivy
- **Docker Security**: Container security analysis
- **Comprehensive Test**: Full test suite with coverage validation
- **Integration Test**: End-to-end API testing
- **Performance Test**: Lightweight performance validation

### 3. Manual Deployment (`manual-deploy.yml`)
**Triggers**: Manual dispatch with parameters

**Features**:
- Environment selection (staging/production)
- Optional test execution
- Optional load testing
- Custom deployment configuration

## 🔧 Setup Instructions

### 1. Repository Secrets
Configure the following secrets in GitHub Settings → Secrets and variables → Actions:

| Secret | Description | Example |
|--------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | `mydevproject-468021` |
| `GCP_SA_KEY` | Service Account JSON key | `{\"type\":\"service_account\",...}` |
| `GCS_BUCKET_NAME` | GCS bucket for model files | `my-penguin-api-bucket` |

See [SECRETS.md](./SECRETS.md) for detailed setup instructions.

### 2. GCP Resources
Ensure the following resources exist:
- Artifact Registry repository: `ml-pipeline-repo`
- Service account with appropriate permissions
- GCS bucket with model files

## 📊 Workflow Features

### Automated Testing
- ✅ Unit tests with pytest
- ✅ Code coverage reporting (70% threshold)
- ✅ Integration testing with Docker containers
- ✅ Security vulnerability scanning
- ✅ Performance testing with Locust

### Docker Optimization
- ✅ Multi-stage builds with caching
- ✅ Security scanning of container images
- ✅ Health check validation
- ✅ Multi-platform build support

### Cloud Deployment
- ✅ Automated Cloud Run deployment
- ✅ Environment variable configuration
- ✅ Service URL reporting
- ✅ Deployment verification

### Monitoring & Reporting
- ✅ Coverage reports uploaded to Codecov
- ✅ Load test results as artifacts
- ✅ Security scan results in GitHub Security tab
- ✅ Deployment notifications

## 🔄 Development Workflow

### Standard Development Flow
1. Create feature branch from `develop`
2. Make changes and push to branch
3. Create PR to `develop` or `main`
4. PR validation workflows run automatically
5. Review and merge PR
6. Main branch deployment runs automatically

### Manual Deployment Flow
1. Go to Actions → Manual Deployment
2. Click \"Run workflow\"
3. Select environment and options
4. Monitor deployment progress
5. Access deployed service URL

## 📈 Performance Benchmarks

The workflows include automated performance testing with the following targets:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time | < 200ms | 95th percentile |
| Throughput | > 20 RPS | Sustained load |
| Error Rate | < 1% | Under normal load |
| Test Coverage | ≥ 70% | Unit test coverage |

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify GCP_SA_KEY is complete JSON
   - Check service account permissions
   - Ensure project ID is correct

2. **Build Failures**
   - Check Dockerfile syntax
   - Verify base image availability
   - Review dependency versions

3. **Deployment Issues**
   - Confirm Artifact Registry exists
   - Verify Cloud Run service permissions
   - Check regional settings

4. **Test Failures**
   - Review test logs in Actions tab
   - Check coverage threshold settings
   - Verify test data and fixtures

### Debug Commands

```bash
# Local testing
uv run pytest -v tests/
docker build -t test .
docker run -p 8080:8080 -e GCS_BUCKET_NAME= test

# GCP authentication test
gcloud auth list
gcloud projects list
gcloud run services list --region=us-east1
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run CI/CD](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)

## 🤝 Contributing

When contributing to this repository:

1. Follow the established workflow patterns
2. Update tests for new functionality  
3. Maintain code coverage above 70%
4. Document any new secrets or configuration
5. Test changes locally before pushing

The CI/CD pipeline will automatically validate your changes and deploy approved updates to production.