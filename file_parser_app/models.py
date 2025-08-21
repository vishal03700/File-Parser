import uuid
from django.db import models
from django.utils import timezone


class UploadedFile(models.Model):
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    progress = models.IntegerField(default=0)
    file_content = models.BinaryField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_filename} ({self.status})"


class ParsedContent(models.Model):
    file = models.OneToOneField(UploadedFile, on_delete=models.CASCADE, related_name='parsed_content')
    content = models.JSONField()
    content_type = models.CharField(max_length=50)  # csv, excel, pdf, etc.
    row_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Parsed content for {self.file.original_filename}"