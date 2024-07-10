from django.db import models
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


storage = None
upload_to = "uploaded_files/"

if settings.USE_S3_STORAGE:
    storage = S3Boto3Storage()
    upload_to = None

FILE_FIELD = models.FileField(storage=storage, upload_to=upload_to)


class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = FILE_FIELD
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    last_updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'uploaded_file'
        db_table_comment = "Table to store uploaded files"
        ordering = ["name"]

    def __str__(self):
        return self.name

