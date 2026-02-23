from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
from firebase_admin import auth

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_welcome_email(request):
    print("----- Attempting to send email -----") # Debug log
    try:
        data = request.data
        email = data.get('email')
        name = data.get('name')
        user_id = data.get('user_id')
        department = data.get('department')

        print(f"Target Email: {email}") # Debug log
        print(f"User ID: {user_id}")    # Debug log
        
        if not email or not user_id:
            print("Error: Missing email or user_id")
            return Response({'error': 'Email and User ID are required'}, status=400)

        subject = f'Welcome to Digital Library System - Your User ID: {user_id}'
        message = f"""
Dear {name},

Your registration with the Digital Library System was successful.

Below are your account details for future reference:

User ID: {user_id}
Department: {department}
Registered Email: {email}

Please keep your User ID secure, as it will be required to access library services, borrow digital resources, and manage your account.

If you have any questions or require assistance, feel free to contact the Digital Library Support Team.

We look forward to supporting your learning and research journey.

⚠️ This is an automated message from Digital Library noreply@digitallibrary.com.
Please do not reply to this email.

Best regards,
Digital Library Team
        """

        # Send email
        print(f"DEBUG: Attempting to send email to {email} via {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"DEBUG: Using SSL: {settings.EMAIL_USE_SSL}, Using TLS: {settings.EMAIL_USE_TLS}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        print("----- Email sent successfully -----")

        return Response({'status': 'success', 'message': 'Email sent successfully'})

    except Exception as e:
        print(f"!!!!! FAILED TO SEND EMAIL !!!!!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Failed to send email: {e}")
        return Response({
            'error': str(e),
            'type': 'EmailSendingError',
            'detail': 'SMTP Timeout or Configuration Issue. Check Railway Environment Variables.',
            'version': getattr(settings, 'BUILD_VERSION', 'local')
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_password_reset_email(request):
    print("----- Attempting to send password reset email -----")
    try:
        data = request.data
        email = data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        # 1. Fetch User Profile from MySQL
        try:
            from .models import UserProfile
            user = UserProfile.objects.get(email=email)
            user_id = user.student_id or "User"
            print(f"Found user {user_id} for email {email}")
        except UserProfile.DoesNotExist:
            print(f"No user found in MySQL for email {email}")
            return Response({
                'error': 'This email is not registered with the Digital Library System.'
            }, status=404)

        # 2. Generate Password Reset Link
        reset_link = auth.generate_password_reset_link(email)
        print(f"Generated reset link for {email}")

        # 3. Construct Email
        subject = f'Reset Your Password for Digital Library System'
        message = f"""
Hello,

We received a request to reset your password for the Digital Library System account associated with your User ID: {user_id}.

You can reset your password by following this link:

{reset_link}

If you did not request this change, you can safely ignore this email. Your password will remain unchanged.

Thanks,
Digital Library Support Team

⚠️ This is an automated message. Please do not reply to this email.
        """

        # 4. Send Email
        print("Sending password reset mail now...")
        print(f"DEBUG: Attempting to send email to {email} via {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"DEBUG: Using SSL: {settings.EMAIL_USE_SSL}, Using TLS: {settings.EMAIL_USE_TLS}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        print("----- Password reset email sent successfully -----")

        return Response({'status': 'success', 'message': 'Password reset email sent'})

    except Exception as e:
        print(f"!!!!! FAILED TO SEND PASSWORD RESET EMAIL !!!!!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Failed to send password reset email: {e}")
        return Response({
            'error': str(e),
            'type': 'EmailSendingError',
            'detail': 'SMTP Timeout or Configuration Issue. Check Railway Environment Variables.',
            'version': getattr(settings, 'BUILD_VERSION', 'local')
        }, status=500)
