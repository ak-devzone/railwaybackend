import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

print(f"DEBUG: Configured DB Name: {settings.DATABASES['default']['NAME']}")

from api.models import AdminProfile, UserProfile

try:
    print("Attempting to count AdminProfiles...")
    count = AdminProfile.objects.count()
    print(f"Success! AdminProfile count: {count}")
    
    print("Attempting to count UserProfiles...")
    u_count = UserProfile.objects.count()
    print(f"Success! UserProfile count: {u_count}")

except Exception as e:
    print(f"FAILED: {e}")
