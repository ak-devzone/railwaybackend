import os
import sys
import django
from django.conf import settings
from pathlib import Path
from dotenv import load_dotenv

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from api.views_email import send_password_reset_email

def verify_reset_email():
    print("--- Verifying Custom Password Reset Email ---")
    
    # Mock request data - use a real email that exists in Firestore if possible
    # Based on the user's request, cse0002 for ak.csproject@gmail.com
    factory = APIRequestFactory()
    data = {
        'email': 'ak.csproject@gmail.com'
    }
    request = factory.post('/api/send-password-reset-email/', data, format='json')
    
    print(f"Mocking request for email: {data['email']}")
    
    try:
        response = send_password_reset_email(request)
        
        if response.status_code == 200:
             print("\nSUCCESS: send_password_reset_email returned 200 OK")
             print("Check the console output above for the generated reset link and User ID retrieval.")
        else:
             print(f"\nFAILURE: send_password_reset_email returned status {response.status_code}")
             print(f"Response data: {response.data}")

    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_reset_email()
