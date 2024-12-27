import os
from typing import List, Set, Optional, Union, Tuple, Dict
from werkzeug.utils import secure_filename
from flask import current_app, request
from datetime import datetime
import magic
import hashlib
from dataclasses import dataclass
from pathlib import Path
from .storage import StorageManager, StorageConfig

@dataclass
class FileValidationResult:
    """Data class to hold file validation results."""
    is_valid: bool
    message: str
    details: Dict[str, any]

class FileValidator:
    """Handles file validation with advanced mime type checking."""
    
    # Common MIME types and their extensions
    MIME_TYPES = {
        # Images
        'image/jpeg': {'.jpg', '.jpeg'},
        'image/png': {'.png'},
        'image/gif': {'.gif'},
        'image/webp': {'.webp'},
        # Documents
        'application/pdf': {'.pdf'},
        'application/msword': {'.doc'},
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {'.docx'},
        'application/vnd.ms-excel': {'.xls'},
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {'.xlsx'},
        # Archives
        'application/zip': {'.zip'},
        'application/x-rar-compressed': {'.rar'},
        # Text
        'text/plain': {'.txt'},
        'text/csv': {'.csv'},
    }

    def __init__(self, allowed_mime_types: Optional[List[str]] = None):
        """Initialize the validator with allowed MIME types.
        
        Args:
            allowed_mime_types: List of allowed MIME types. If None, all known types are allowed.
        """
        self.allowed_mime_types = allowed_mime_types or list(self.MIME_TYPES.keys())
        
    def validate_mime_type(self, file_stream) -> FileValidationResult:
        """Validate file MIME type using python-magic.
        
        Args:
            file_stream: File-like object to validate
            
        Returns:
            FileValidationResult: Validation result with details
        """
        try:
            # Read first 2048 bytes for MIME detection
            header = file_stream.read(2048)
            file_stream.seek(0)  # Reset file pointer
            
            mime_type = magic.from_buffer(header, mime=True)
            
            if mime_type not in self.allowed_mime_types:
                return FileValidationResult(
                    is_valid=False,
                    message="File type not allowed",
                    details={
                        'detected_mime': mime_type,
                        'allowed_mimes': self.allowed_mime_types
                    }
                )
            
            return FileValidationResult(
                is_valid=True,
                message="Valid file type",
                details={'mime_type': mime_type}
            )
        except Exception as e:
            return FileValidationResult(
                is_valid=False,
                message=f"Error validating file type: {str(e)}",
                details={'error': str(e)}
            )

class FileUploader:
    """A professional file uploader for Flask applications with advanced validation."""
    
    def __init__(
        self,
        upload_folder: Union[str, Path],
        allowed_mime_types: Optional[List[str]] = None,
        max_content_length: int = 16 * 1024 * 1024,  # 16MB default
        use_timestamp: bool = True,
        hash_filenames: bool = False,
        storage_config: Optional[dict] = None
    ):
        """Initialize the FileUploader.
        
        Args:
            upload_folder (Union[str, Path]): Base directory for file storage
            allowed_mime_types (List[str], optional): List of allowed MIME types
            max_content_length (int): Maximum allowed file size in bytes
            use_timestamp (bool): Whether to prefix filenames with timestamps
            hash_filenames (bool): Whether to hash filenames for uniqueness
            storage_config (dict, optional): Additional storage configuration options
                - create_date_subfolders (bool): Create date-based subfolder structure
                - max_folder_size (int): Maximum total storage size in bytes
                - backup_old_files (bool): Whether to backup files before overwriting
                - backup_folder (str): Path to store backups
                - path_template (str): Template for date-based paths
        """
        # Initialize storage manager
        storage_config = storage_config or {}
        self.storage = StorageManager(StorageConfig(
            base_path=Path(upload_folder),
            create_date_subfolders=storage_config.get('create_date_subfolders', False),
            max_folder_size=storage_config.get('max_folder_size'),
            backup_old_files=storage_config.get('backup_old_files', False),
            backup_folder=Path(storage_config['backup_folder']) if storage_config.get('backup_folder') else None,
            path_template=storage_config.get('path_template', '{year}/{month}/{day}')
        ))
        
        self.validator = FileValidator(allowed_mime_types)
        self.max_content_length = max_content_length
        self.use_timestamp = use_timestamp
        self.hash_filenames = hash_filenames
        
        # Ensure upload directory exists
        self.storage.config.base_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, file_stream, original_filename: str) -> str:
        """Generate a secure filename with optional timestamp and hashing.
        
        Args:
            file_stream: File-like object for hashing if needed
            original_filename: Original filename
            
        Returns:
            str: Secure filename
        """
        filename = secure_filename(original_filename)
        name, ext = os.path.splitext(filename)
        
        if self.hash_filenames:
            # Generate SHA-256 hash of file content
            file_stream.seek(0)
            content_hash = hashlib.sha256(file_stream.read()).hexdigest()[:12]
            file_stream.seek(0)
            name = f"{name}_{content_hash}"
            
        if self.use_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name = f"{timestamp}_{name}"
            
        return f"{name}{ext}"
    
    def validate_file(self, file_stream) -> FileValidationResult:
        """Validate a file stream.
        
        Args:
            file_stream: File-like object to validate
            
        Returns:
            FileValidationResult: Validation result
        """
        # Check file size
        file_stream.seek(0, 2)  # Seek to end
        size = file_stream.tell()
        file_stream.seek(0)  # Reset pointer
        
        if size > self.max_content_length:
            return FileValidationResult(
                is_valid=False,
                message=f"File exceeds maximum size of {self.max_content_length/1024/1024}MB",
                details={'size': size, 'max_size': self.max_content_length}
            )
            
        # Validate MIME type
        return self.validator.validate_mime_type(file_stream)
    
    def save_file(self, file, custom_filename: str = None) -> Tuple[bool, str, Optional[str], Dict]:
        """Save a single file with validation.
        
        Args:
            file: File object from request.files
            custom_filename (str, optional): Custom filename to use
            
        Returns:
            Tuple[bool, str, Optional[str], Dict]: (success, message, filename if successful, details)
        """
        if not file:
            return False, "No file provided", None, {}
            
        filename = custom_filename or file.filename
        if not filename:
            return False, "No filename provided", None, {}
            
        # Validate file
        validation_result = self.validate_file(file)
        if not validation_result.is_valid:
            return False, validation_result.message, None, validation_result.details
            
        try:
            # Generate secure filename
            filename = self._generate_filename(file, filename)
            
            # Get file size for quota check
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            # Save file using storage manager
            success, message, filepath = self.storage.save_file(file, filename, file_size)
            
            if not success:
                return False, message, None, {}
                
            return True, "File uploaded successfully", filepath.name, {
                'mime_type': validation_result.details.get('mime_type'),
                'size': file_size,
                'path': str(filepath.relative_to(self.storage.config.base_path))
            }
        except Exception as e:
            return False, f"Error saving file: {str(e)}", None, {'error': str(e)}

    def save_files(self, files) -> List[dict]:
        """Save multiple files with validation.
        
        Args:
            files: List of file objects from request.files
            
        Returns:
            List[dict]: List of results for each file upload
        """
        results = []
        for file in files:
            success, message, filename, details = self.save_file(file)
            results.append({
                'success': success,
                'message': message,
                'filename': filename,
                'original_filename': file.filename,
                'details': details
            })
        return results
    
    def handle_request(self, file_key: str = 'file') -> Union[dict, List[dict]]:
        """Handle file upload request automatically.
        
        Args:
            file_key (str): Key to look for in request.files
            
        Returns:
            Union[dict, List[dict]]: Upload results
        """
        if file_key not in request.files:
            return {'success': False, 'message': 'No file part in the request'}
            
        files = request.files.getlist(file_key)
        
        if len(files) == 1:
            success, message, filename, details = self.save_file(files[0])
            return {
                'success': success,
                'message': message,
                'filename': filename,
                'original_filename': files[0].filename,
                'details': details
            }
        
        return self.save_files(files)

    def get_storage_stats(self) -> dict:
        """Get storage usage statistics.
        
        Returns:
            dict: Storage statistics
        """
        return self.storage.get_storage_usage()

    def list_uploaded_files(self, pattern: str = "*") -> List[dict]:
        """List all uploaded files matching a pattern.
        
        Args:
            pattern (str): Glob pattern to match files
            
        Returns:
            List[dict]: List of file information
        """
        files = self.storage.list_files(pattern)
        return [{
            'filename': f.name,
            'path': str(f.relative_to(self.storage.config.base_path)),
            'size': f.stat().st_size,
            'modified': datetime.fromtimestamp(f.stat().st_mtime)
        } for f in files]
