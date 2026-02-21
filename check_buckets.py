import firebase_admin
from firebase_admin import credentials, storage
import os

# Path to service account key
cred_path = 'firebase-credentials.json'
if not os.path.exists(cred_path):
    cred_path = '../firebase-credentials.json'

if not os.path.exists(cred_path):
    print(f"Error: {cred_path} not found.")
    exit(1)

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

print(f"Project ID: {cred.project_id}")

from google.cloud import storage as gcs

print("\nAttempting to list all buckets in the project...")
try:
    # storage.client() returns the underlying google.cloud.storage.Client
    # But firebase_admin doesn't expose it directly in a documented way easily for listing?
    # Actually initializing firebase_admin with credentials sets up the environment.
    # We can just use gcs.Client with the credentials.
    
    gcs_client = gcs.Client(credentials=cred.get_credential(), project=cred.project_id)
    buckets = list(gcs_client.list_buckets())
    
    if not buckets:
        print("No buckets found in this project.")
    else:
        print(f"Found {len(buckets)} buckets:")
        for b in buckets:
            print(f" - {b.name}")
            
except Exception as e:
    print(f"Error listing buckets: {e}")
