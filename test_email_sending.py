import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

def test_email():
    print(f"Testing email with HOST: {settings.EMAIL_HOST}, USER: {settings.EMAIL_HOST_USER}")
    try:
        subject = 'Test Email from Digital Library System'
        message = 'This is a test email to verify SMTP configuration.'
        recipient_list = [settings.EMAIL_HOST_USER] # Send to self
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        print("SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")

if __name__ == '__main__':
    test_email()
