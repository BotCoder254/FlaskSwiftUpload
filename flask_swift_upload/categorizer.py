"""Intelligent file categorization system for FlaskSwiftUpload."""

from typing import Dict, Optional, Set, List
from pathlib import Path
import magic
import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileCategory:
    """File category with metadata."""
    name: str
    mime_types: Set[str]
    extensions: Set[str]
    max_size: int
    description: str
    allowed_users: Optional[Set[str]] = None
    requires_validation: bool = False

class FileCategorizer:
    """Intelligent file categorization system."""

    DEFAULT_CATEGORIES = {
        'images': FileCategory(
            name='images',
            mime_types={'image/jpeg', 'image/png', 'image/gif', 'image/webp'},
            extensions={'.jpg', '.jpeg', '.png', '.gif', '.webp'},
            max_size=10 * 1024 * 1024,  # 10MB
            description='Image files (JPEG, PNG, GIF, WebP)'
        ),
        'documents': FileCategory(
            name='documents',
            mime_types={
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            },
            extensions={'.pdf', '.doc', '.docx'},
            max_size=50 * 1024 * 1024,  # 50MB
            description='Document files (PDF, DOC, DOCX)',
            requires_validation=True
        ),
        'archives': FileCategory(
            name='archives',
            mime_types={
                'application/zip',
                'application/x-rar-compressed',
                'application/x-7z-compressed'
            },
            extensions={'.zip', '.rar', '.7z'},
            max_size=100 * 1024 * 1024,  # 100MB
            description='Archive files (ZIP, RAR, 7Z)',
            requires_validation=True
        )
    }

    def __init__(self, custom_categories: Optional[Dict[str, FileCategory]] = None):
        """Initialize the file categorizer.
        
        Args:
            custom_categories: Optional custom category definitions
        """
        self.categories = custom_categories or self.DEFAULT_CATEGORIES
        self.magic = magic.Magic(mime=True)

    def categorize_file(self, file_path: Path) -> Optional[FileCategory]:
        """Categorize a file based on its content and metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[FileCategory]: Matching category or None
        """
        if not file_path.exists():
            return None

        # Get MIME type from content
        mime_type = self.magic.from_file(str(file_path))
        extension = file_path.suffix.lower()

        # Find matching category
        for category in self.categories.values():
            if (mime_type in category.mime_types and
                extension in category.extensions):
                return category

        return None

    def get_storage_path(self, category: FileCategory, filename: str) -> Path:
        """Get the appropriate storage path for a file.
        
        Args:
            category: File category
            filename: Original filename
            
        Returns:
            Path: Storage path for the file
        """
        now = datetime.now()
        return Path(
            category.name,
            str(now.year),
            f"{now.month:02d}",
            filename
        )

    def validate_category_access(
        self,
        category: FileCategory,
        user: Optional[str] = None
    ) -> bool:
        """Validate if a user has access to a category.
        
        Args:
            category: File category
            user: Optional user identifier
            
        Returns:
            bool: True if access is allowed
        """
        if not category.allowed_users:
            return True
        return user in category.allowed_users if user else False

    def get_category_stats(self) -> Dict[str, Dict]:
        """Get statistics for each category.
        
        Returns:
            Dict: Category statistics
        """
        stats = {}
        for name, category in self.categories.items():
            stats[name] = {
                'description': category.description,
                'max_size': category.max_size,
                'allowed_types': list(category.mime_types),
                'requires_validation': category.requires_validation
            }
        return stats

    def suggest_category(self, filename: str, mime_type: str) -> List[str]:
        """Suggest possible categories for a file.
        
        Args:
            filename: Filename to analyze
            mime_type: File's MIME type
            
        Returns:
            List[str]: List of suggested category names
        """
        suggestions = []
        extension = Path(filename).suffix.lower()
        
        for name, category in self.categories.items():
            if (mime_type in category.mime_types or
                extension in category.extensions):
                suggestions.append(name)
                
        return suggestions
