import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from api.models import DatabaseFile

def list_files():
    print("Listing Database Files:")
    files = DatabaseFile.objects.all()
    if not files:
        print("No files found in database.")
        return

    for f in files:
        print(f"ID: {f.id} | Name: '{f.name}' | Size: {f.size}")

if __name__ == '__main__':
    list_files()
