import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from api.models import UserProfile

try:
    uid = 'test_user_123'
    if UserProfile.objects.filter(uid=uid).exists():
        print(f"User {uid} already exists. Deleting...")
        UserProfile.objects.get(uid=uid).delete()

    print(f"Creating user {uid}...")
    user = UserProfile.objects.create(
        uid=uid,
        email='test@example.com',
        name='Test User',
        role='student',
        department='CSE',
        student_id='CSE999',
        mobile='1234567890',
        profile_completed=True
    )
    print(f"User created: {user}")

    # Verify read
    u = UserProfile.objects.get(uid=uid)
    print(f"Read back user: {u.name} ({u.email}) from DB.")

    # Clean up
    u.delete()
    print("Test user deleted.")
    print("Health check: Database write/read successful.")

except Exception as e:
    print(f"Database Error: {e}")
