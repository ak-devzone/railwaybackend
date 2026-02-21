import os
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

def test_storage():
    print("Testing Database Storage...")
    filename = 'test_db_file.txt'
    content = b'This is a test file stored in MySQL.'
    
    # Clean up if exists
    if default_storage.exists(filename):
        default_storage.delete(filename)
        print(f"Deleted existing {filename}")

    # Save
    name = default_storage.save(filename, ContentFile(content))
    print(f"Saved file as: {name}")
    
    # Verify existence
    if default_storage.exists(name):
        print(f"File {name} exists in storage.")
    else:
        print(f"ERROR: File {name} not found in storage.")
        return

    # Read content
    f = default_storage.open(name)
    read_content = f.read()
    print(f"Read content: {read_content}")
    
    if read_content == content:
        print("SUCCESS: Content matches.")
    else:
        print("ERROR: Content mismatch.")

    # Check URL
    url = default_storage.url(name)
    print(f"File URL: {url}")
    
    # Clean up
    default_storage.delete(name)
    print("Cleaned up test file.")

if __name__ == '__main__':
    test_storage()
