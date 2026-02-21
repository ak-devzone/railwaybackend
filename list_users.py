"""
Script to list all users in Firestore
Usage: python list_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from firebase_admin import firestore

def list_users():
    """List all users"""
    db = firestore.client()
    users = db.collection('users').stream()
    
    print("\nStarting user listing...")
    count = 0
    for user in users:
        count += 1
        data = user.to_dict()
        print(f"----------------------------------------")
        print(f"User ID: {user.id}")
        print(f"Email: {data.get('email', 'N/A')}")
        print(f"Name: {data.get('name', 'N/A')}")
        print(f"Role: {data.get('role', 'N/A')}")
        
    if count == 0:
        print("\nNo users found in database.")
    else:
        print(f"\nTotal users found: {count}")

if __name__ == '__main__':
    list_users()
