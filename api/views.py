import os
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    import socket
    smtp_diagnostics = {}
    host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    
    # 1. DNS Check
    try:
        ips = socket.gethostbyname_ex(host)
        smtp_diagnostics['dns_lookup'] = ips[2]
    except Exception as e:
        smtp_diagnostics['dns_lookup'] = f"Failed: {str(e)}"

    # 2. Port Check (Wait 3s)
    def check_port(p):
        try:
            with socket.create_connection((host, p), timeout=3):
                return "OPEN"
        except Exception as e:
            return f"CLOSED ({str(e)})"
            
    smtp_diagnostics['port_465'] = check_port(465)
    smtp_diagnostics['port_587'] = check_port(587)

    return Response({
        'status': 'healthy',
        'version': getattr(settings, 'BUILD_VERSION', 'unknown'),
        'database': 'connected',
        'smtp_host': host,
        'smtp_diagnostics': smtp_diagnostics
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
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        print(f"Admin welcome email sent to {email}")
        return Response({'message': 'Welcome email sent successfully'})
    except Exception as e:
        print(f"Error sending admin welcome email: {e}")
        return Response({'error': str(e)}, status=500)
