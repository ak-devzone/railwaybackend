from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from .models import DatabaseFile
import mimetypes
import io

def serve_database_file(request, filename):
    try:
        db_file = get_object_or_404(DatabaseFile, name=filename)
        
        # Guess content type
        content_type, encoding = mimetypes.guess_type(filename)
        content_type = content_type or 'application/octet-stream'
        
        response = HttpResponse(db_file.content, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        if params := request.GET.get('download'):
             response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    except Exception as e:
        raise Http404("File not found")
