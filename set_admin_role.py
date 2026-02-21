"""
Script to set a user's role to 'admin' in Firestore
Usage: python set_admin_role.py <email>
"""

import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from firebase_admin import auth, firestore

def set_admin_role(email):
    """Set user role to admin by email"""
    db = firestore.client()
    
    # 1. Try to find user in Firebase Auth
    try:
        user_record = auth.get_user_by_email(email)
        uid = user_record.uid
        print(f"\nFound user in Firebase Auth:")
        print(f"   UID: {uid}")
        print(f"   Email: {user_record.email}")
    except auth.UserNotFoundError:
        print(f"\nError: No user found in Firebase Auth with email: {email}")
        print("Please ensure you have registered/logged in with this email.")
        return False
    except Exception as e:
        print(f"\nError lookup up user: {e}")
        return False

    # 2. Check/Create user in Firestore
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        print(f"   Firestore document exists. Updating role...")
        user_ref.update({'role': 'admin'})
    else:
        print(f"   Firestore document missing. Creating new admin user...")
        user_ref.set({
            'email': email,
            'role': 'admin',
            'name': user_record.display_name or 'Admin',
            'createdAt': firestore.SERVER_TIMESTAMP
        })
    
    print(f"\nSuccessfully updated role to 'admin'")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python set_admin_role.py <email>")
        print("Example: python set_admin_role.py admin@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    print(f"\nSearching for user with email: {email}")
    
    success = set_admin_role(email)
    
    if success:
        print("\nDone! You can now login and upload books.")
        print("   Please refresh your browser and try again.")
    else:
        print("\nFailed to update user role.")
        sys.exit(1)
