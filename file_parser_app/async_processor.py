import threading
import time
import logging
from django.utils import timezone
from .models import UploadedFile, ParsedContent
from .file_parser import FileParser
from .progress_tracker import progress_tracker

logger = logging.getLogger(__name__)


class AsyncFileProcessor:
    """Asynchronous file processor with progress tracking."""
    
    @staticmethod
    def process_file_async(file_id: str):
        """Process a file asynchronously in a separate thread."""
        thread = threading.Thread(
            target=AsyncFileProcessor._process_file_worker,
            args=(file_id,),
            daemon=True
        )
        thread.start()
    
    @staticmethod
    def _process_file_worker(file_id: str):
        """Worker function that processes the file."""
        try:
            # Get file from database
            uploaded_file = UploadedFile.objects.get(id=file_id)
            
            # Update status to processing
            uploaded_file.status = 'processing'
            uploaded_file.progress = 0
            uploaded_file.save()
            progress_tracker.set_progress(file_id, 0, 'processing')
            
            # Simulate processing time and progress updates
            for progress in [10, 25, 50, 75, 90]:
                time.sleep(0.5)  # Simulate processing time
                uploaded_file.progress = progress
                uploaded_file.save()
                progress_tracker.set_progress(file_id, progress, 'processing')
            
            # Parse the file
            logger.info(f"Starting to parse file: {uploaded_file.original_filename}")
            
            parse_result = FileParser.parse_file(
                uploaded_file.file_content,
                uploaded_file.file_type,
                uploaded_file.original_filename
            )
            
            if parse_result['success']:
                # Save parsed content
                ParsedContent.objects.create(
                    file=uploaded_file,
                    content=parse_result['data'],
                    content_type=parse_result['content_type'],
                    row_count=AsyncFileProcessor._count_rows(parse_result['data'])
                )
                
                # Update file status to ready
                uploaded_file.status = 'ready'
                uploaded_file.progress = 100
                uploaded_file.error_message = None
                uploaded_file.save()
                progress_tracker.set_progress(file_id, 100, 'ready')
                
                logger.info(f"Successfully parsed file: {uploaded_file.original_filename}")
            else:
                # Update file status to failed
                uploaded_file.status = 'failed'
                uploaded_file.error_message = parse_result['error']
                uploaded_file.save()
                progress_tracker.set_status(file_id, 'failed')
                
                logger.error(f"Failed to parse file: {uploaded_file.original_filename}, Error: {parse_result['error']}")
        
        except UploadedFile.DoesNotExist:
            logger.error(f"File with ID {file_id} not found")
        except Exception as e:
            logger.error(f"Unexpected error processing file {file_id}: {str(e)}")
            try:
                uploaded_file = UploadedFile.objects.get(id=file_id)
                uploaded_file.status = 'failed'
                uploaded_file.error_message = f"Processing error: {str(e)}"
                uploaded_file.save()
                progress_tracker.set_status(file_id, 'failed')
            except:
                pass
    
    @staticmethod
    def _count_rows(parsed_data: dict) -> int:
        """Count rows in parsed data."""
        if 'rows' in parsed_data:
            return len(parsed_data['rows'])
        elif 'sheets' in parsed_data:
            return parsed_data.get('total_rows', 0)
        elif 'pages' in parsed_data:
            return parsed_data.get('total_pages', 0)
        else:
            return 0