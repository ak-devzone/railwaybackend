import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from api.models import Book
from api.views_books import get_book_details
from rest_framework.test import APIRequestFactory

def debug_books():
    print("Listing Books...")
    books = Book.objects.all()
    
    if not books.exists():
        print("No books found in DB.")
        return
        
    for book in books:
        print(f"Found Book: ID='{book.id}', Title='{book.title}'")
        
        # Try to get details manually
        try:
            b = Book.objects.get(id=book.id)
            print(f"  [Direct DB] Success: Found {b.title}")
        except Book.DoesNotExist:
            print(f"  [Direct DB] Failed: DoesNotExist")
            
        # Try to call the view (simulate request)
        # Note: We can't easily simulate the view here without DRF context, but we can check the DB lookup logic.
        # The view logic is: Book.objects.get(id=book_id)
        
    print("-" * 20)
    print("Checking DatabaseFile for PDF...")
    from api.models import DatabaseFile
    for book in books:
        if book.pdf_file:
            print(f"Book: {book.title}")
            print(f"  PDF Field: '{book.pdf_file.name}'")
            # Check if this file exists in DatabaseFile
            exists = DatabaseFile.objects.filter(name=book.pdf_file.name).exists()
            print(f"  Exists in DatabaseFile? {exists}")
            
            # Also check if it exists with 'books/pdfs/' prefix if missing
            if not exists and not book.pdf_file.name.startswith('books/pdfs/'):
                 alt_name = f"books/pdfs/{book.pdf_file.name}"
                 alt_exists = DatabaseFile.objects.filter(name=alt_name).exists()
                 print(f"  Checking '{alt_name}'? {alt_exists}")

if __name__ == '__main__':
    debug_books()
