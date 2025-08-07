# 🚀 Simple CI/CD Guide

This project uses a **simplified GitHub Actions workflow** that works out of the box without complex setup.

## ✅ What It Does

### **Automatic Testing (No Setup Required)**
When you push code or create a PR, GitHub Actions will:

1. **Test the Application**
   - Install Python dependencies
   - Run unit tests
   - Build Docker image

2. **Test the Container**
   - Start the API in a container
   - Test health endpoint (`GET /`)
   - Test prediction endpoint (`POST /predict`)
   - Verify responses

3. **Load Test**
   - Run basic performance tests
   - Generate load test report
   - Upload results as artifacts

## 🎯 How to Use

### **Push to Main Branch**
```bash
git add .
git commit -m "Your changes"
git push origin main
```
→ **Triggers full CI/CD pipeline**

### **Create Pull Request**
```bash
git checkout -b feature-branch
git push origin feature-branch
# Create PR via GitHub UI
```
→ **Triggers testing pipeline**

### **View Results**
1. Go to **Actions** tab in GitHub
2. Click on your workflow run
3. See test results and logs
4. Download load test report from **Artifacts**

## 📊 What Success Looks Like

### ✅ **All Tests Pass**
- Unit tests complete
- Docker container starts successfully
- API endpoints respond correctly
- Load tests generate performance data

### ❌ **If Tests Fail**
- Check the **Actions** tab logs
- Common issues:
  - Python dependency conflicts
  - Docker build problems
  - API endpoint failures
  - Load test timeouts

## 🔧 No Configuration Needed

This simplified CI/CD requires **NO** setup:
- ❌ No GCP secrets needed
- ❌ No service account keys
- ❌ No bucket configuration
- ❌ No Cloud Run deployment

**It just works!** 🎉

## 📈 Load Test Results

After each run:
1. Go to **Actions** → Your workflow run
2. Scroll to **Artifacts** section  
3. Download `simple-load-test-report`
4. Open `simple-load-test-report.html` in browser
5. View detailed performance metrics

## 🚀 Next Steps

Once this simple CI/CD is working, you can:
1. **Enable cloud deployment** by adding GCP secrets
2. **Increase test coverage** by adding more tests
3. **Add code quality** checks (linting, formatting)
4. **Implement security** scanning

But for now, this gives you a **working CI/CD pipeline** immediately! ✨