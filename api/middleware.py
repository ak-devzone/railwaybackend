"""
Firebase Authentication Middleware
Validates Firebase ID tokens from frontend requests
"""

from django.http import JsonResponse
from firebase_admin import auth, firestore
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthenticationMiddleware:
    """
    Middleware to verify Firebase ID tokens sent from the frontend
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for certain paths
        excluded_paths = ['/admin/', '/api/health/']
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            id_token = auth_header.split('Bearer ')[1]
            
            try:
                # Verify the ID token
                decoded_token = auth.verify_id_token(id_token)
                request.user_data = decoded_token
                request.firebase_user = decoded_token
                request.user_uid = decoded_token['uid']
                
                # Check for suspension and get user role from MySQL
                from api.models import UserProfile
                try:
                    user_profile = UserProfile.objects.get(uid=decoded_token['uid'])
                    
                    if user_profile.is_suspended:
                        from django.core.exceptions import PermissionDenied
                        raise PermissionDenied("Account suspended")
                    
                    # Merge MySQL data into request.user_data
                    request.user_data['role'] = user_profile.role
                    request.user_data['department'] = user_profile.department
                    request.user_data['semester'] = user_profile.semester
                    request.user_data['name'] = user_profile.name
                    request.user_data['email'] = user_profile.email
                    request.user_data['mysql_id'] = user_profile.uid
                    
                    print(f"DEBUG: Middleware found user data for UID {decoded_token['uid']}: {user_profile}")
                    
                except UserProfile.DoesNotExist:
                    # Check if Admin
                    from api.models import AdminProfile
                    try:
                        admin_profile = AdminProfile.objects.get(uid=decoded_token['uid'])
                        request.user_data['role'] = 'admin'
                        request.user_data['name'] = admin_profile.name
                        request.user_data['email'] = admin_profile.email
                        request.user_data['mysql_id'] = admin_profile.uid
                        print(f"DEBUG: Middleware found Admin for UID {decoded_token['uid']}")
                    except AdminProfile.DoesNotExist:
                        print(f"DEBUG: User {decoded_token['uid']} not found in MySQL (User or Admin)")
                        # User not in MySQL yet (e.g. new user or profile not completed)
                        # We still allow the request to proceed, but they won't have a role (defaulting to 'student' in views if needed)
                        request.user_data['role'] = 'student'
                
            except Exception as e:
                logger.error(f"Firebase token verification failed: {e}")
                pass
        
        response = self.get_response(request)
        return response


class RemoveXFrameOptionsMiddleware:
    """
    Middleware to explicitly remove X-Frame-Options header
    to allow PDF embedding in iframes
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Force removal of the header if it exists
        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']
        return response
