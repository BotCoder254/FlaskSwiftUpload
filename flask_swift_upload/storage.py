from pathlib import Path
from typing import Optional, Union, List
import os
import shutil
from datetime import datetime
import re
from dataclasses import dataclass

@dataclass
class StorageConfig:
    """Configuration for file storage."""
    base_path: Path
    create_date_subfolders: bool = False
    max_folder_size: Optional[int] = None  # in bytes
    backup_old_files: bool = False
    backup_folder: Optional[Path] = None
    path_template: str = "{year}/{month}/{day}"

class StorageManager:
    """Manages file storage with advanced path handling and security features."""

    UNSAFE_PATTERNS = [
        r'\.\.',  # Directory traversal
        r'^[/\\]',  # Absolute paths
        r'[\x00-\x1f]',  # Control characters
        r'[<>:"|?*]'  # Windows/Unix reserved characters
    ]

    def __init__(self, config: StorageConfig):
        """Initialize the storage manager.
        
        Args:
            config (StorageConfig): Storage configuration
        """
        self.config = config
        self._ensure_storage_structure()

    def _ensure_storage_structure(self):
        """Ensure storage directories exist and are properly configured."""
        self.config.base_path.mkdir(parents=True, exist_ok=True)
        if self.config.backup_old_files and self.config.backup_folder:
            self.config.backup_folder.mkdir(parents=True, exist_ok=True)

    def _is_safe_path(self, path: str) -> bool:
        """Check if a path is safe to use.
        
        Args:
            path (str): Path to check
            
        Returns:
            bool: True if path is safe, False otherwise
        """
        return not any(re.search(pattern, path) for pattern in self.UNSAFE_PATTERNS)

    def _get_storage_path(self, filename: str) -> Path:
        """Get the storage path for a file based on configuration.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            Path: Full path where the file should be stored
        """
        if not self.config.create_date_subfolders:
            return self.config.base_path / filename

        now = datetime.now()
        path_vars = {
            'year': str(now.year),
            'month': f"{now.month:02d}",
            'day': f"{now.day:02d}",
            'hour': f"{now.hour:02d}",
        }
        
        relative_path = self.config.path_template.format(**path_vars)
        full_path = self.config.base_path / relative_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        return full_path / filename

    def _check_storage_quota(self, file_size: int) -> bool:
        """Check if storing a file would exceed the storage quota.
        
        Args:
            file_size (int): Size of the file to store
            
        Returns:
            bool: True if file can be stored, False if it would exceed quota
        """
        if not self.config.max_folder_size:
            return True

        total_size = sum(f.stat().st_size for f in self.config.base_path.rglob('*') if f.is_file())
        return (total_size + file_size) <= self.config.max_folder_size

    def _backup_existing_file(self, file_path: Path):
        """Backup an existing file if backup is enabled.
        
        Args:
            file_path (Path): Path to the file to backup
        """
        if not (self.config.backup_old_files and self.config.backup_folder and file_path.exists()):
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.config.backup_folder / backup_name
        shutil.copy2(file_path, backup_path)

    def save_file(self, file_stream, filename: str, file_size: int) -> tuple[bool, str, Optional[Path]]:
        """Save a file to storage with all configured options.
        
        Args:
            file_stream: File-like object to save
            filename (str): Name of the file
            file_size (int): Size of the file in bytes
            
        Returns:
            tuple[bool, str, Optional[Path]]: Success status, message, and path if successful
        """
        if not self._is_safe_path(filename):
            return False, "Invalid filename or path detected", None

        if not self._check_storage_quota(file_size):
            return False, "Storage quota would be exceeded", None

        try:
            storage_path = self._get_storage_path(filename)
            self._backup_existing_file(storage_path)
            
            with storage_path.open('wb') as f:
                shutil.copyfileobj(file_stream, f)
            
            return True, "File saved successfully", storage_path
        except Exception as e:
            return False, f"Error saving file: {str(e)}", None

    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get the path to a stored file.
        
        Args:
            filename (str): Name of the file to locate
            
        Returns:
            Optional[Path]: Path to the file if found, None otherwise
        """
        if not self._is_safe_path(filename):
            return None

        # Search in all possible storage locations
        for path in self.config.base_path.rglob(filename):
            if path.is_file():
                return path
        return None

    def list_files(self, pattern: str = "*") -> List[Path]:
        """List all files in storage matching a pattern.
        
        Args:
            pattern (str): Glob pattern to match files
            
        Returns:
            List[Path]: List of matching file paths
        """
        return [p for p in self.config.base_path.rglob(pattern) if p.is_file()]

    def get_storage_usage(self) -> dict:
        """Get storage usage statistics.
        
        Returns:
            dict: Storage statistics including total size and file count
        """
        files = list(self.config.base_path.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        return {
            'total_size': total_size,
            'file_count': len([f for f in files if f.is_file()]),
            'quota': self.config.max_folder_size,
            'quota_used': (total_size / self.config.max_folder_size * 100) 
                if self.config.max_folder_size else None
        }
