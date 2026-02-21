from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import AdminProfile
import json
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def register_admin(request):
    """
    Register a new admin.
    Expects JSON body:
    - uid (from auth token preferably, or passed in body if authorized by middleware)
    - name
    - email
    - secret_key (for audit, though validated on frontend/middleware)
    """
    try:
        # Check authentication (Middleware should have attached user_data)
        if not hasattr(request, 'user_data'):
             return JsonResponse({'error': 'Unauthorized'}, status=401)
             
        uid = request.user_data['uid']
        data = json.loads(request.body)
        
        name = data.get('name')
        email = data.get('email')
        secret_key = data.get('secretKey') # Optional to store for audit
        
        if not all([name, email]):
             return JsonResponse({'error': 'Missing required fields'}, status=400)
             
        # Check if admin already exists
        if AdminProfile.objects.filter(uid=uid).exists():
             return JsonResponse({'error': 'Admin already registered'}, status=400)

        # Create AdminProfile
        admin = AdminProfile.objects.create(
            uid=uid,
            name=name,
            email=email,
            role='admin',
            secret_key_used=secret_key
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Admin registered successfully',
            'admin': {
                'id': admin.uid,
                'name': admin.name,
                'email': admin.email,
                'role': admin.role
            }
        })
        
    except Exception as e:
        logger.error(f"Error registering admin: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_admin_details(request, admin_id):
    """Get admin details"""
    try:
        try:
            admin = AdminProfile.objects.get(uid=admin_id)
        except AdminProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Admin not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'user': { # Returning as 'user' to match frontend expectation
                'id': admin.uid,
                'name': admin.name,
                'email': admin.email,
                'role': admin.role,
                'createdAt': admin.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting admin details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
