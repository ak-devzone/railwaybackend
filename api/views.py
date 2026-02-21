from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})

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

You can login at: http://localhost:5173/admin/login

If you have any questions or need assistance, please contact the system administrator.

Best regards,
Digital Library System Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response({'message': 'Welcome email sent successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
