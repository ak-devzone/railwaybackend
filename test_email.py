import os
import sys
import django
from django.conf import settings
from pathlib import Path
from dotenv import load_dotenv

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
# Explicitly load .env
load_dotenv(BASE_DIR / '.env')

sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.core.mail import send_mail

def test_email():
    print("--- Django Email Configuration Test ---")
    print(f"BASE_DIR: {BASE_DIR}")
    
    # Check variables directly from os.environ
    host_user_env = os.getenv('EMAIL_HOST_USER')
    host_password_env = os.getenv('EMAIL_HOST_PASSWORD')
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    print(f"EMAIL_HOST_USER (env): {host_user_env}")
    print(f"EMAIL_HOST_USER (settings): {settings.EMAIL_HOST_USER}")
    
    if host_password_env:
        print(f"EMAIL_HOST_PASSWORD (env): {'*' * len(host_password_env)} (Length: {len(host_password_env)})")
    else:
        print("EMAIL_HOST_PASSWORD (env): None (Check your .env file!)")

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\nERROR: Email credentials are missing. Please check your .env file.")
        print("Make sure 'EMAIL_HOST_USER' and 'EMAIL_HOST_PASSWORD' are set in:")
        print(f"{BASE_DIR / '.env'}")
        return

    recipient = settings.EMAIL_HOST_USER
    print(f"\nAttempting to send test email to: {recipient}...")

    try:
        send_mail(
            'Test Email from Digital Library System',
            'This is a test email to verify SMTP configuration.',
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        print("\nSUCCESS: Email sent successfully!")
        print(f"Check the inbox of {recipient}")
    except Exception as e:
        print("\nFAILURE: Could not send email.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
        if "Authentication Required" in str(e):
            print("\nSUGGESTION: This error usually means:")
            print("1. Default password used instead of App Password.")
            print("2. 2-Step Verification not enabled on Google Account.")
            print("3. Typo in email/password.")

if __name__ == '__main__':
    test_email()
