import os
from django.http import JsonResponse
from firebase_admin import firestore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'healthy',
        'version': getattr(settings, 'BUILD_VERSION', 'unknown'),
        'database': 'connected',
        'email_system': 'Firestore Queue'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def send_admin_welcome(request):
    """Send welcome email to newly registered admin"""
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        
        if not name or not email:
            return Response({'error': 'Name and email are required'}, status=400)
        
        subject = 'Welcome to Digital Library System - Admin Account Created'
        message = f"""
Dear {name},

Welcome to the Digital Library System!

Your admin account has been successfully created. You can now access the admin panel to manage the library system.

Account Details:
- Email: {email}
- Role: Administrator

You can login at: https://library-systemm.web.app/login

If you have any questions or need assistance, please contact the system administrator.

Best regards,
Digital Library System Team
        """
        
        # Queue email in Firestore
        db = firestore.client()
        db.collection('mail').add({
            'to': [email],
            'message': {
                'subject': subject,
                'text': message,
                'html': message.replace('\n', '<br>')
            },
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        
        print(f"Admin welcome email queued in Firestore for {email}")
        return Response({'message': 'Welcome email queued successfully'})
    except Exception as e:
        print(f"Error sending admin welcome email: {e}")
        return Response({'error': str(e)}, status=500)
