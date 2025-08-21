import logging
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import UploadedFile, ParsedContent
from .serializers import (
    UploadedFileSerializer, 
    FileListSerializer, 
    FileProgressSerializer,
    ParsedContentSerializer
)
from .async_processor import AsyncFileProcessor
from .progress_tracker import progress_tracker

logger = logging.getLogger(__name__)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """Upload a file and start processing."""
    try:
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        
        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_obj.size > max_size:
            return Response(
                {'error': f'File too large. Maximum size is {max_size // (1024*1024)}MB'}, 
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        
        # Create file record
        serializer = UploadedFileSerializer(data={'file': file_obj})
        if serializer.is_valid():
            uploaded_file = serializer.save()
            
            # Initialize progress tracking
            progress_tracker.set_progress(str(uploaded_file.id), 0, 'uploading')
            
            # Start async processing
            AsyncFileProcessor.process_file_async(str(uploaded_file.id))
            
            logger.info(f"File uploaded successfully: {uploaded_file.original_filename}")
            
            return Response({
                'file_id': uploaded_file.id,
                'filename': uploaded_file.original_filename,
                'status': uploaded_file.status,
                'message': 'File uploaded successfully and processing started'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return Response(
            {'error': 'Internal server error during file upload'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_file_progress(request, file_id):
    """Get upload/processing progress for a file."""
    try:
        # Try to get from database first
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        
        # Check in-memory progress tracker for real-time updates
        progress_data = progress_tracker.get_progress(file_id)
        
        if progress_data:
            # Use in-memory data if available (more up-to-date)
            response_data = {
                'file_id': file_id,
                'status': progress_data.get('status', uploaded_file.status),
                'progress': progress_data.get('progress', uploaded_file.progress)
            }
        else:
            # Fall back to database data
            response_data = {
                'file_id': file_id,
                'status': uploaded_file.status,
                'progress': uploaded_file.progress
            }
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Error getting progress for file {file_id}: {str(e)}")
        return Response(
            {'error': 'File not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_file_content(request, file_id):
    """Get parsed file content."""
    try:
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        
        if uploaded_file.status == 'ready':
            try:
                parsed_content = uploaded_file.parsed_content
                serializer = ParsedContentSerializer(parsed_content)
                
                return Response({
                    'file_id': file_id,
                    'filename': uploaded_file.original_filename,
                    'status': uploaded_file.status,
                    'parsed_content': serializer.data
                })
            except ParsedContent.DoesNotExist:
                return Response(
                    {'error': 'Parsed content not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response({
                'message': 'File upload or processing in progress. Please try again later.',
                'status': uploaded_file.status,
                'progress': uploaded_file.progress
            }, status=status.HTTP_202_ACCEPTED)
    
    except Exception as e:
        logger.error(f"Error getting file content for {file_id}: {str(e)}")
        return Response(
            {'error': 'File not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_files(request):
    """List all uploaded files."""
    try:
        files = UploadedFile.objects.all()
        serializer = FileListSerializer(files, many=True)
        
        return Response({
            'files': serializer.data,
            'total_count': files.count()
        })
    
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_file(request, file_id):
    """Delete a file and its parsed content."""
    try:
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        filename = uploaded_file.original_filename
        
        # Remove from progress tracker
        progress_tracker.remove_progress(file_id)
        
        # Delete file and related content (CASCADE will handle ParsedContent)
        uploaded_file.delete()
        
        logger.info(f"File deleted successfully: {filename}")
        
        return Response({
            'message': f'File "{filename}" deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        return Response(
            {'error': 'File not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )