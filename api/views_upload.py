from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from .models import UserProfile
import logging
import uuid
import os

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_id_proof(request):
    try:
        # Check if file is present
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
            
        file_obj = request.FILES['file']
        user_id = request.data.get('userId', '') # This is likely student_id (e.g. CSE001) or UID?
        # Frontend sends userData.userId which is student_id.
        
        # File size validation (512KB max)
        max_size = 512 * 1024  # 512KB in bytes
        if file_obj.size > max_size:
            return Response({
                'error': f'File size not proper. Maximum allowed size is 512KB. Your file is {file_obj.size / 1024:.1f}KB.'
            }, status=400)
        
        # File format validation
        allowed_extensions = ['pdf', 'jpg', 'jpeg']
        file_extension = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''
        
        if file_extension not in allowed_extensions:
            return Response({
                'error': f'File format not proper. Only PDF, JPG, and JPEG files are allowed.'
            }, status=400)
            
        # Try to link to user profile
        user_profile = None
        if user_id:
            try:
                # Try finding by student_id first, then uid
                user_profile = UserProfile.objects.filter(student_id=user_id).first()
                if not user_profile:
                     user_profile = UserProfile.objects.filter(uid=user_id).first()
            except Exception as e:
                logger.warning(f"Error finding user for upload: {e}")
        
        if user_profile:
            # Save file to model
            user_profile.id_proof.save(f"{user_profile.uid}_{uuid.uuid4()}.{file_extension}", file_obj)
            user_profile.save()
            file_url = request.build_absolute_uri(user_profile.id_proof.url)
        else:
            # Fallback to saving without link (legacy behavior support if no user found)
            # But better to error or just save to tmp?
            # Let's save it to media/id-proofs manually to support current frontend flow 
            # where it uploads THEN updates user doc.
            from django.core.files.storage import FileSystemStorage
            media_root = os.path.join(settings.MEDIA_ROOT, 'id-proofs')
            os.makedirs(media_root, exist_ok=True)
            fs = FileSystemStorage(location=media_root)
            filename = f'temp_{uuid.uuid4()}.{file_extension}'
            saved_filename = fs.save(filename, file_obj)
            file_url = request.build_absolute_uri(settings.MEDIA_URL + 'id-proofs/' + saved_filename)
        
        return Response({
            'status': 'success',
            'url': file_url
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return Response({'error': str(e)}, status=500)
