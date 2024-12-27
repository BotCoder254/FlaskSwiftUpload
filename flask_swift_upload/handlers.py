"""Advanced file handling utilities for FlaskSwiftUpload."""

import os
from typing import List, Dict, Optional, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .validators import ValidationResult, ContentValidator, FileNameValidator

@dataclass
class FileMetadata:
    """Metadata for uploaded files."""
    original_filename: str
    mime_type: str
    size: int
    hash: str
    upload_time: datetime
    category: str
    validation_status: ValidationResult

class BatchUploadManager:
    """Handles batch file uploads with advanced features."""
    
    def __init__(self, max_concurrent_uploads: int = 5):
        """Initialize the batch upload manager.
        
        Args:
            max_concurrent_uploads: Maximum number of concurrent uploads
        """
        self.max_concurrent_uploads = max_concurrent_uploads
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_uploads)
        self._upload_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'total_size': 0
        }

    async def process_batch(
        self,
        files: List[BinaryIO],
        validators: List[Union[ContentValidator, FileNameValidator]]
    ) -> Dict[str, List[Dict]]:
        """Process a batch of files asynchronously.
        
        Args:
            files: List of file objects to process
            validators: List of validators to apply
            
        Returns:
            Dict containing successful and failed uploads
        """
        tasks = []
        for file in files:
            task = asyncio.create_task(self._process_single_file(file, validators))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Organize results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        self._update_stats(successful, failed)
        
        return {
            'successful': successful,
            'failed': failed,
            'stats': self._upload_stats
        }

    async def _process_single_file(
        self,
        file: BinaryIO,
        validators: List[Union[ContentValidator, FileNameValidator]]
    ) -> Dict:
        """Process a single file with validation.
        
        Args:
            file: File object to process
            validators: List of validators to apply
            
        Returns:
            Dict containing processing results
        """
        try:
            # Calculate file hash
            file_hash = await self._calculate_file_hash(file)
            
            # Validate file
            validation_results = []
            for validator in validators:
                result = await self._run_validator(validator, file)
                validation_results.append(result)
                if not result.is_valid:
                    return {
                        'success': False,
                        'filename': getattr(file, 'filename', 'unknown'),
                        'error': result.message,
                        'details': result.details
                    }
            
            return {
                'success': True,
                'filename': file.filename,
                'hash': file_hash,
                'validation_results': validation_results
            }
        except Exception as e:
            return {
                'success': False,
                'filename': getattr(file, 'filename', 'unknown'),
                'error': str(e)
            }

    async def _calculate_file_hash(self, file: BinaryIO) -> str:
        """Calculate SHA-256 hash of file content asynchronously.
        
        Args:
            file: File object to hash
            
        Returns:
            str: File hash
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._hash_file,
            file
        )

    def _hash_file(self, file: BinaryIO) -> str:
        """Calculate file hash (runs in thread pool).
        
        Args:
            file: File to hash
            
        Returns:
            str: File hash
        """
        hasher = hashlib.sha256()
        for chunk in iter(lambda: file.read(65536), b''):
            hasher.update(chunk)
        file.seek(0)
        return hasher.hexdigest()

    async def _run_validator(
        self,
        validator: Union[ContentValidator, FileNameValidator],
        file: BinaryIO
    ) -> ValidationResult:
        """Run a validator asynchronously.
        
        Args:
            validator: Validator to run
            file: File to validate
            
        Returns:
            ValidationResult: Validation result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._validate_file,
            validator,
            file
        )

    def _validate_file(
        self,
        validator: Union[ContentValidator, FileNameValidator],
        file: BinaryIO
    ) -> ValidationResult:
        """Run validation (runs in thread pool).
        
        Args:
            validator: Validator to use
            file: File to validate
            
        Returns:
            ValidationResult: Validation result
        """
        if isinstance(validator, ContentValidator):
            return validator.validate_content(file)
        elif isinstance(validator, FileNameValidator):
            return validator.validate_filename(file.filename)
        raise ValueError(f"Unsupported validator type: {type(validator)}")

    def _update_stats(self, successful: List[Dict], failed: List[Dict]):
        """Update upload statistics.
        
        Args:
            successful: List of successful uploads
            failed: List of failed uploads
        """
        self._upload_stats['total_processed'] += len(successful) + len(failed)
        self._upload_stats['successful'] += len(successful)
        self._upload_stats['failed'] += len(failed)
        self._upload_stats['total_size'] += sum(
            os.path.getsize(s['filename']) for s in successful if os.path.exists(s['filename'])
        )
