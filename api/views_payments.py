"""
Payment and Purchase Management Views
Handles payment initiation, verification, and purchase tracking
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import firestore
from datetime import datetime
import os

# Note: Install razorpay with: pip install razorpay
# For now, we'll create placeholder functions that can be integrated later

db = firestore.client()

@api_view(['POST'])
def initiate_payment(request, book_id):
    """
    Initiate payment for a premium book
    Creates a payment order and returns details for frontend
    """
    try:
        if not hasattr(request, 'user_data'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.user_data.get('uid')
        
        # Get book details
        book_ref = db.collection('books').document(book_id)
        book = book_ref.get()
        
        if not book.exists:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        book_data = book.to_dict()
        
        # Check if book is premium
        if not book_data.get('isPremium', False):
            return Response({'error': 'This book is free'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already purchased
        existing_purchase = db.collection('purchases').where('userId', '==', user_id).where('bookId', '==', book_id).limit(1).get()
        if len(list(existing_purchase)) > 0:
            return Response({'error': 'Book already purchased'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Integrate with Razorpay
        # For now, return mock payment data
        order_data = {
            'orderId': f'order_{book_id}_{user_id}',
            'amount': book_data.get('price', 0),
            'currency': 'INR',
            'bookId': book_id,
            'bookTitle': book_data.get('title'),
            'description': f'Purchase of {book_data.get("title")}',
            # In production, add Razorpay key and other details
        }
        
        return Response({
            'order': order_data,
            'message': 'Payment order created successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_payment(request, book_id):
    """
    Verify payment and grant access to book
    """
    try:
        if not hasattr(request, 'user_data'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.user_data.get('uid')
        
        # Get payment details from request
        payment_id = request.data.get('paymentId')
        order_id = request.data.get('orderId')
        signature = request.data.get('signature')
        
        if not all([payment_id, order_id]):
            return Response({'error': 'Missing payment details'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get book details
        book_ref = db.collection('books').document(book_id)
        book = book_ref.get()
        
        if not book.exists:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        book_data = book.to_dict()
        
        # TODO: Verify payment signature with Razorpay
        # For now, we'll assume payment is valid
        
        # Create purchase record
        purchase_data = {
            'userId': user_id,
            'bookId': book_id,
            'bookTitle': book_data.get('title'),
            'amount': book_data.get('price', 0),
            'paymentId': payment_id,
            'orderId': order_id,
            'purchasedAt': firestore.SERVER_TIMESTAMP,
            'status': 'completed'
        }
        
        db.collection('purchases').add(purchase_data)
        
        return Response({
            'message': 'Payment verified successfully',
            'hasAccess': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_purchases(request):
    """
    Get all purchases for the current user
    """
    try:
        if not hasattr(request, 'user_data'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.user_data.get('uid')
        
        # Get all purchases for user
        purchases_ref = db.collection('purchases').where('userId', '==', user_id).order_by('purchasedAt', direction=firestore.Query.DESCENDING)
        purchases = purchases_ref.stream()
        
        purchases_list = []
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            purchase_data['id'] = purchase.id
            purchases_list.append(purchase_data)
        
        return Response({
            'purchases': purchases_list,
            'count': len(purchases_list)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_my_library(request):
    """
    Get all books accessible to the user (free + purchased)
    """
    try:
        if not hasattr(request, 'user_data'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.user_data.get('uid')
        
        # Get all free books
        free_books_ref = db.collection('books').where('isPremium', '==', False)
        free_books = free_books_ref.stream()
        
        library = []
        for book in free_books:
            book_data = book.to_dict()
            book_data['accessType'] = 'free'
            library.append(book_data)
        
        # Get purchased books
        purchases_ref = db.collection('purchases').where('userId', '==', user_id)
        purchases = purchases_ref.stream()
        
        purchased_book_ids = [p.to_dict().get('bookId') for p in purchases]
        
        # Get details of purchased books
        for book_id in purchased_book_ids:
            book_ref = db.collection('books').document(book_id)
            book = book_ref.get()
            if book.exists:
                book_data = book.to_dict()
                book_data['accessType'] = 'purchased'
                library.append(book_data)
        
        return Response({
            'library': library,
            'count': len(library)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
