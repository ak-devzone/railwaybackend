from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Book, Purchase, UserProfile
import uuid
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_book(request):
    """
    Upload a new book
    Admin only endpoint
    """
    try:
        # Verify admin role
        user_role = getattr(request, 'user_data', {}).get('role')
        if user_role != 'admin':
            return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Extract form data
        title = request.data.get('title')
        author = request.data.get('author')
        description = request.data.get('description', '')
        isbn = request.data.get('isbn', '')
        department = request.data.get('department')
        semester = request.data.get('semester')
        is_premium = request.data.get('isPremium', 'false').lower() == 'true'
        price = float(request.data.get('price', 0)) if is_premium else 0
        tags = request.data.get('tags', '')
        featured = request.data.get('featured', 'false').lower() == 'true'
        
        # Validate required fields
        if not all([title, author, department, semester]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get uploaded files
        cover_image = request.FILES.get('coverImage')
        pdf_file = request.FILES.get('pdfFile')
        
        if not cover_image or not pdf_file:
            return Response({'error': 'Both cover image and PDF file are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate PDF size (max 25 MB)
        MAX_PDF_SIZE = 25 * 1024 * 1024
        if pdf_file.size > MAX_PDF_SIZE:
            size_mb = pdf_file.size / (1024 * 1024)
            return Response({
                'error': f'PDF file is too large ({size_mb:.1f} MB). Maximum allowed size is 25 MB. Please compress or split your PDF.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate cover image size (max 2 MB)
        MAX_COVER_SIZE = 2 * 1024 * 1024
        if cover_image.size > MAX_COVER_SIZE:
            size_mb = cover_image.size / (1024 * 1024)
            return Response({
                'error': f'Cover image is too large ({size_mb:.1f} MB). Maximum allowed size is 2 MB.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Book
        book_id = str(uuid.uuid4())
        file_size_mb = round(pdf_file.size / (1024 * 1024), 2)
        
        book = Book.objects.create(
            id=book_id,
            title=title,
            author=author,
            description=description,
            isbn=isbn,
            department=department,
            semester=semester,
            is_premium=is_premium,
            price=price,
            tags=tags,
            featured=featured,
            uploaded_by=request.user_data.get('uid', 'unknown'),
            file_size=f'{file_size_mb} MB',
            cover_image=cover_image,
            pdf_file=pdf_file
        )
        
        # Return book data
        book_data = {
            'id': book.id,
            'title': book.title,
            'coverImageUrl': request.build_absolute_uri(book.cover_image.url),
            'pdfUrl': request.build_absolute_uri(book.pdf_file.url),
            'department': book.department,
            'semester': book.semester,
            'price': book.price
        }
        
        return Response({
            'message': 'Book uploaded successfully',
            'book': book_data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error uploading book: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_books(request):
    """
    List all books with optional filtering
    """
    try:
        department = request.GET.get('department')
        semester = request.GET.get('semester')
        is_premium = request.GET.get('isPremium')
        search = request.GET.get('search', '')
        featured = request.GET.get('featured')
        
        books_queryset = Book.objects.all().order_by('-uploaded_at')
        
        if department:
            books_queryset = books_queryset.filter(department=department)
        if semester:
            books_queryset = books_queryset.filter(semester=semester)
        if is_premium is not None:
            is_premium_bool = is_premium.lower() == 'true'
            books_queryset = books_queryset.filter(is_premium=is_premium_bool)
        if featured is not None:
             featured_bool = featured.lower() == 'true'
             books_queryset = books_queryset.filter(featured=featured_bool)
        if search:
            books_queryset = books_queryset.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search) | 
                Q(isbn__icontains=search)
            )
            
        books_list = []
        for book in books_queryset:
            books_list.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'department': book.department,
                'semester': book.semester,
                'coverImageUrl': request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
                'pdfUrl': request.build_absolute_uri(book.pdf_file.url) if book.pdf_file else None,
                'isPremium': book.is_premium,
                'price': book.price,
                'featured': book.featured,
                'fileSize': book.file_size,
                'uploadedAt': book.uploaded_at
            })
            
        return Response({
            'books': books_list,
            'count': len(books_list)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing books: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_book_details(request, book_id):
    """
    Get detailed information about a specific book
    """
    try:
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'isbn': book.isbn,
            'department': book.department,
            'semester': book.semester,
            'coverImageUrl': request.build_absolute_uri(book.cover_image.url) if book.cover_image else None,
            'pdfUrl': request.build_absolute_uri(book.pdf_file.url) if book.pdf_file else None,
            'isPremium': book.is_premium,
            'price': book.price,
            'featured': book.featured,
            'fileSize': book.file_size,
            'tags': book.tags.split(',') if book.tags else []
        }
        
        # Check access
        has_access, access_reason = _check_access(request, book)
                
        return Response({
            'book': book_data,
            'hasAccess': has_access,
            'accessReason': access_reason
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _check_access(request, book):
    """Helper to check if user has access to book"""
    user_id = getattr(request, 'user_data', {}).get('uid')
    
    # 1. Check ID Proof for Logged In Users (Priority over everything)
    if user_id:
        try:
            user_profile = UserProfile.objects.get(uid=user_id)
            if not user_profile.id_proof:
                return False, 'missing_id_proof'
        except UserProfile.DoesNotExist:
             return False, 'missing_id_proof'

    # 2. Free books
    if not book.is_premium:
        return True, 'free'
        
    # 3. Premium books (Logged in check purchase)
    if user_id:
        # Check purchase
        if Purchase.objects.filter(user__uid=user_id, book=book).exists():
             return True, 'purchased'
             
    # Default denied
    return False, 'not-purchased'


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_book(request, book_id):
    """
    Update book details
    """
    try:
        user_role = getattr(request, 'user_data', {}).get('role')
        if user_role != 'admin':
            return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
             
        # Update fields
        if 'title' in request.data: book.title = request.data['title']
        if 'author' in request.data: book.author = request.data['author']
        if 'description' in request.data: book.description = request.data['description']
        if 'isbn' in request.data: book.isbn = request.data['isbn']
        if 'department' in request.data: book.department = request.data['department']
        if 'semester' in request.data: book.semester = request.data['semester']
        if 'isPremium' in request.data: 
            book.is_premium = request.data['isPremium'].lower() == 'true' if isinstance(request.data['isPremium'], str) else request.data['isPremium']
        if 'price' in request.data: book.price = float(request.data['price'])
        if 'tags' in request.data: book.tags = request.data['tags']
        if 'featured' in request.data:
            book.featured = request.data['featured'].lower() == 'true' if isinstance(request.data['featured'], str) else request.data['featured']

        # Optional file replacement
        if 'coverImage' in request.FILES:
            if book.cover_image:
                book.cover_image.delete(save=False)  # remove old DatabaseFile row
            book.cover_image = request.FILES['coverImage']
        if 'pdfFile' in request.FILES:
            if book.pdf_file:
                book.pdf_file.delete(save=False)  # remove old DatabaseFile row
            book.pdf_file = request.FILES['pdfFile']
            
        book.save()
        
        return Response({
            'message': 'Book updated successfully',
            'book': {
                'id': book.id,
                'title': book.title
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_book(request, book_id):
    """
    Delete a book
    """
    try:
        user_role = getattr(request, 'user_data', {}).get('role')
        if user_role != 'admin':
            return Response({'error': 'Unauthorized. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            book = Book.objects.get(id=book_id)
            # Clean up stored files from DatabaseStorage before deleting the record
            if book.pdf_file:
                book.pdf_file.delete(save=False)
            if book.cover_image:
                book.cover_image.delete(save=False)
            book.delete()
        except Book.DoesNotExist:
             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
             
        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
        
    except Exception as e:
         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_book_access(request, book_id):
    """
    Check access
    """
    try:
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
             
        has_access, access_reason = _check_access(request, book)
        
        return Response({
            'hasAccess': has_access,
            'reason': access_reason # Frontend expects 'reason'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
