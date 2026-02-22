import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from api.models import UserProfile

def test_lookup():
    email = 'noreplydigitallibrarysystemm@gmail.com' # Use an email that should exist or we can create temporarily
    print(f"Testing lookup for email: {email}")
    try:
        user = UserProfile.objects.get(email=email)
        print(f"✅ Found user: {user.name}, Student ID: {user.student_id}")
    except UserProfile.DoesNotExist:
        print(f"❌ User with email {email} not found in MySQL.")
    except Exception as e:
        print(f"❌ Error during lookup: {e}")

if __name__ == '__main__':
    test_lookup()
