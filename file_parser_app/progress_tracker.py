import threading
from typing import Dict, Optional


class ProgressTracker:
    """In-memory progress tracker for file uploads and processing."""
    
    def __init__(self):
        self._progress_data: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def set_progress(self, file_id: str, progress: int, status: str = None):
        """Update progress for a file."""
        with self._lock:
            if file_id not in self._progress_data:
                self._progress_data[file_id] = {}
            
            self._progress_data[file_id]['progress'] = max(0, min(100, progress))
            
            if status:
                self._progress_data[file_id]['status'] = status
    
    def get_progress(self, file_id: str) -> Optional[Dict]:
        """Get progress data for a file."""
        with self._lock:
            return self._progress_data.get(file_id, None)
    
    def remove_progress(self, file_id: str):
        """Remove progress data for a file."""
        with self._lock:
            self._progress_data.pop(file_id, None)
    
    def set_status(self, file_id: str, status: str):
        """Update status for a file."""
        with self._lock:
            if file_id not in self._progress_data:
                self._progress_data[file_id] = {}
            self._progress_data[file_id]['status'] = status


# Global progress tracker instance
progress_tracker = ProgressTracker()