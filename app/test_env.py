from dotenv import load_dotenv
import os

print("Testing .env loading...")
result = load_dotenv(".env")
print(f"load_dotenv result: {result}")

print("\nEnvironment variables:")
print(f"GCS_BUCKET_NAME: '{os.getenv('GCS_BUCKET_NAME')}'")
print(f"GCS_MODEL_PATH: '{os.getenv('GCS_MODEL_PATH')}'")
print(f"GCS_METADATA_PATH: '{os.getenv('GCS_METADATA_PATH')}'")
print(f"GOOGLE_APPLICATION_CREDENTIALS: '{os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}'")

bucket_name = os.getenv("GCS_BUCKET_NAME", "")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
use_gcs = bucket_name and credentials_path
print(f"\nuse_gcs decision: {use_gcs}")

# Test if credentials file exists
if credentials_path:
    print(f"Credentials file exists: {os.path.exists(credentials_path)}")