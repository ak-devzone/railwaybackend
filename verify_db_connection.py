import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

print(f"Configured Database Name: {settings.DATABASES['default']['NAME']}")
print(f"Configured Database User: {settings.DATABASES['default']['USER']}")
