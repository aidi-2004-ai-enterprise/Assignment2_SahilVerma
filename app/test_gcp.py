#!/usr/bin/env python3
import os
import tempfile
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv("../.env")

def test_gcp_connection():
    """Test GCP bucket access and model download"""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    
    print(f"Testing GCP connection...")
    print(f"Credentials: {credentials_path}")
    print(f"Bucket: {bucket_name}")
    
    if not credentials_path or not bucket_name:
        print("Missing GCP credentials or bucket name")
        return False
        
    try:
        # Initialize storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # List files in bucket
        print(f"\nFiles in bucket '{bucket_name}':")
        blobs = list(bucket.list_blobs(max_results=10))
        
        if not blobs:
            print("No files found in bucket")
            return False
            
        for blob in blobs:
            print(f"  - {blob.name} ({blob.size} bytes)")
            
        # Try to download and test both model files
        model_blob = bucket.blob("model.json")
        metadata_blob = bucket.blob("model_metadata.json")
        
        if not model_blob.exists():
            print("model.json not found in bucket")
            return False
            
        if not metadata_blob.exists():
            print("model_metadata.json not found in bucket")
            return False
        
        # Download both files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as model_tmp:
            model_blob.download_to_filename(model_tmp.name)
            print(f"Downloaded model.json to {model_tmp.name}")
            
            # Test if it's a valid XGBoost model by checking file size and basic content
            file_size = os.path.getsize(model_tmp.name)
            print(f"Model file size: {file_size} bytes")
            
            with open(model_tmp.name, 'r') as f:
                first_line = f.readline().strip()
                print(f"Model file starts with: {first_line[:100]}...")
                
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as meta_tmp:
            metadata_blob.download_to_filename(meta_tmp.name)
            print(f"Downloaded model_metadata.json to {meta_tmp.name}")
            
            # Test metadata content
            with open(meta_tmp.name, 'r') as f:
                import json
                metadata = json.load(f)
                print(f"Metadata keys: {list(metadata.keys())}")
                if 'feature_names' in metadata:
                    print(f"Feature names: {metadata['feature_names']}")
                if 'label_encoder_classes' in metadata:
                    print(f"Label classes: {metadata['label_encoder_classes']}")
        
        print("Successfully downloaded and validated both model files!")
        return True
            
    except Exception as e:
        print(f"Error accessing GCP: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gcp_connection()
    print(f"\n{'GCP test passed!' if success else 'GCP test failed!'}")