from rest_framework import serializers
from .models import UploadedFile, ParsedContent


class UploadedFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)
    original_filename = serializers.CharField(read_only=True)  # explicitly read-only
    
    class Meta:
        model = UploadedFile
        fields = [
            'id', 'filename', 'original_filename', 'file_size', 
            'file_type', 'status', 'progress', 'created_at', 
            'updated_at', 'error_message', 'file'
        ]
        read_only_fields = [
            'id', 'filename', 'file_size', 'file_type', 
            'status', 'progress', 'created_at', 'updated_at', 'error_message', 'original_filename'
        ]
    
    def create(self, validated_data):
        file_obj = validated_data.pop('file', None)
        if file_obj:
            validated_data['original_filename'] = file_obj.name
            validated_data['filename'] = file_obj.name
            validated_data['file_size'] = file_obj.size
            validated_data['file_type'] = file_obj.content_type or 'application/octet-stream'
            validated_data['file_content'] = file_obj.read()
        
        return super().create(validated_data)



class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'filename', 'original_filename', 'status', 'created_at', 'file_size']


class FileProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'status', 'progress']


class ParsedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedContent
        fields = ['content', 'content_type', 'row_count', 'created_at']