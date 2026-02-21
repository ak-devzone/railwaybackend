
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
import django
django.setup()

from firebase_admin import firestore

def check_admin_roles():
    db = firestore.client()
    users_ref = db.collection('users')
    
    print("-" * 50)
    print("CHECKING ALL USERS FOR ADMIN ROLE")
    print("-" * 50)
    
    users = users_ref.stream()
    found_admin = False
    
    for user in users:
        data = user.to_dict()
        uid = user.id
        role = data.get('role')
        user_role = data.get('userRole')
        email = data.get('email', 'No Email')
        
        is_admin_role = role == 'admin'
        is_admin_user_role = user_role == 'admin'
        
        if is_admin_role or is_admin_user_role:
            found_admin = True
            print(f"[ADMIN FOUND] UID: {uid}")
            print(f"  Email: {email}")
            print(f"  role: {role}")
            print(f"  userRole: {user_role}")
            print("-" * 30)
        else:
            print(f"[User] {uid} | Email: {email} | Role: {role} | UserRole: {user_role}")
            pass

    if not found_admin:
        print("NO ADMINS FOUND IN DATABASE!")

if __name__ == '__main__':
    check_admin_roles()
