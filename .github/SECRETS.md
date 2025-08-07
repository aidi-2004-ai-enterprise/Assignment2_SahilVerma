# GitHub Repository Secrets Setup

This document explains how to configure the required secrets for GitHub Actions CI/CD pipeline.

## Required Secrets

### 1. GCP_PROJECT_ID
**Description**: Your Google Cloud Project ID  
**Value**: `mydevproject-468021` (or your actual project ID)  
**Usage**: Used for Artifact Registry and Cloud Run deployment

### 2. GCP_SA_KEY
**Description**: Service Account JSON key for GitHub Actions  
**Value**: Complete JSON content of your service account key file  
**Usage**: Authentication for Cloud Build, Artifact Registry, and Cloud Run

#### Creating Service Account for GitHub Actions:

```bash
# Create service account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

### 3. GCS_BUCKET_NAME
**Description**: Name of your GCS bucket containing model files  
**Value**: `my-penguin-api-bucket` (or your actual bucket name)  
**Usage**: Environment variable for model loading in production

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value

## Security Best Practices

- ✅ Service account follows principle of least privilege
- ✅ JSON key is stored securely in GitHub Secrets
- ✅ No secrets are hardcoded in workflow files
- ✅ Secrets are only available to authorized workflows

## Verification

After adding secrets, you can verify the setup by:

1. Pushing code to a branch and creating a PR (triggers PR validation)
2. Merging to main branch (triggers full CI/CD pipeline)
3. Checking GitHub Actions tab for workflow results

## Troubleshooting

### Common Issues:

1. **Authentication failed**: Check GCP_SA_KEY format (must be complete JSON)
2. **Permission denied**: Verify service account has all required roles
3. **Resource not found**: Ensure PROJECT_ID and BUCKET_NAME are correct
4. **Build fails**: Check Artifact Registry repository exists in correct region

### Debug Commands:

```bash
# Test service account locally
export GOOGLE_APPLICATION_CREDENTIALS="github-actions-key.json"
gcloud auth application-default print-access-token

# Verify permissions
gcloud projects get-iam-policy YOUR-PROJECT-ID
```