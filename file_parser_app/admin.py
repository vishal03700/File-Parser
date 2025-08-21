from django.contrib import admin
from .models import UploadedFile, ParsedContent


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'status', 'progress', 'file_size', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['original_filename', 'filename']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['file_content']
        return self.readonly_fields


@admin.register(ParsedContent)
class ParsedContentAdmin(admin.ModelAdmin):
    list_display = ['file', 'content_type', 'row_count', 'created_at']
    list_filter = ['content_type', 'created_at']
    readonly_fields = ['created_at']