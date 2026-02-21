import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from firebase_admin import firestore

def set_admin_role():
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <uid_or_email>")
        return

    target = sys.argv[1]
    db = firestore.client()
    users_ref = db.collection('users')
    
    user_doc = None
    uid = None

    # Try to find by UID first
    doc_ref = users_ref.document(target)
    doc = doc_ref.get()
    
    if doc.exists:
        user_doc = doc
        uid = target
        print(f"Found user by UID: {target}")
    else:
        # Try to find by email
        print(f"Searching for user with email: {target}")
        query = users_ref.where('email', '==', target).limit(1)
        results = list(query.stream())
        if results:
            user_doc = results[0]
            uid = user_doc.id
            print(f"Found user by Email: {target} (UID: {uid})")
        else:
            print(f"Error: No user found with UID or Email: {target}")
            return

    if uid:
        print(f"Promoting user {uid} to Admin...")
        users_ref.document(uid).update({
            'role': 'admin',
            'userRole': 'admin'  # Set both to be sure
        })
        print("Success! User updated.")
        
        # Verify
        updated = users_ref.document(uid).get().to_dict()
        print(f"Verification - Role: {updated.get('role')}, UserRole: {updated.get('userRole')}")

if __name__ == '__main__':
    set_admin_role()
