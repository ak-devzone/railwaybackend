import os
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.urls import reverse
from .models import DatabaseFile

@deconstructible
class DatabaseStorage(Storage):
    def _open(self, name, mode='rb'):
        try:
            f = DatabaseFile.objects.get(name=name)
            return ContentFile(f.content, name=name)
        except DatabaseFile.DoesNotExist:
            return None

    def _save(self, name, content):
        name = self.get_available_name(name)
        content_bytes = content.read()
        
        # Determine content type if possible, or store generic
        # For now, simplistic.
        
        DatabaseFile.objects.create(
            name=name,
            content=content_bytes,
            size=len(content_bytes)
        )
        return name

    def exists(self, name):
        return DatabaseFile.objects.filter(name=name).exists()

    def url(self, name):
        # We need a view to serve this file
        return reverse('serve-db-file', args=[name])

    def delete(self, name):
        DatabaseFile.objects.filter(name=name).delete()
