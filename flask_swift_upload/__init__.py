"""
FlaskSwiftUpload - Professional File Upload Module for Flask
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A secure, flexible, and feature-rich file upload module for Flask applications.
Built with modern Python features and enterprise-grade security in mind.
"""

from .uploader import FileUploader
from .storage import StorageManager, StorageConfig
from .validators import ContentValidator, FileNameValidator
from .constants import LOGO, MIME_TYPES

__version__ = "1.0.0"
__author__ = "FlaskSwiftUpload Team"
__license__ = "MIT"

# Export all required classes
__all__ = [
    'FileUploader',
    'StorageManager',
    'StorageConfig',
    'ContentValidator',
    'FileNameValidator',
]

def show_logo():
    """Display the FlaskSwiftUpload ASCII art logo."""
    print(LOGO)
