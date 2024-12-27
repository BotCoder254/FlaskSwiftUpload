"""Advanced validation utilities for FlaskSwiftUpload."""

import re
import magic
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Set, Dict, Any
from dataclasses import dataclass
from .constants import MIME_TYPES, SECURITY, VALIDATION

@dataclass
class ValidationResult:
    """Comprehensive validation result with detailed information."""
    is_valid: bool
    message: str
    details: Dict[str, Any]
    risk_level: str = "low"  # low, medium, high
    validation_type: str = "general"

class ContentValidator:
    """Advanced content validation with security checks."""

    def __init__(self, mime_types: Optional[Dict[str, list]] = None):
        """Initialize the content validator.
        
        Args:
            mime_types: Optional custom MIME type mapping
        """
        self.mime_types = mime_types or {
            mime: ext
            for category in MIME_TYPES.values()
            for mime, ext in category.items()
        }
        self.magic = magic.Magic(mime=True)

    def validate_content(self, file_stream, filename: str) -> ValidationResult:
        """Perform comprehensive content validation.
        
        Args:
            file_stream: File-like object to validate
            filename: Original filename
            
        Returns:
            ValidationResult: Detailed validation result
        """
        # Read header for content checks
        header = file_stream.read(VALIDATION['content_check_size'])
        file_stream.seek(0)

        # Get MIME type
        detected_mime = self.magic.from_buffer(header)
        
        # Perform security checks
        entropy = self._calculate_entropy(header)
        risk_factors = self._assess_risk_factors(header, filename)
        
        # Validate against allowed types
        if detected_mime not in self.mime_types:
            return ValidationResult(
                is_valid=False,
                message="File type not allowed",
                details={
                    'detected_mime': detected_mime,
                    'allowed_mimes': list(self.mime_types.keys()),
                    'entropy': entropy,
                    'risk_factors': risk_factors
                },
                risk_level="high" if risk_factors else "medium",
                validation_type="mime"
            )

        return ValidationResult(
            is_valid=True,
            message="Valid content type",
            details={
                'mime_type': detected_mime,
                'extensions': self.mime_types[detected_mime],
                'entropy': entropy,
                'risk_factors': risk_factors
            },
            risk_level="low" if not risk_factors else "medium",
            validation_type="mime"
        )

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data for anomaly detection.
        
        Args:
            data: Bytes to analyze
            
        Returns:
            float: Entropy value
        """
        if not data:
            return 0.0
            
        entropy = 0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log2(p_x)
        return entropy

    def _assess_risk_factors(self, content: bytes, filename: str) -> list:
        """Assess potential security risks in file content.
        
        Args:
            content: File content to analyze
            filename: Original filename
            
        Returns:
            list: List of identified risk factors
        """
        risks = []
        
        # Check for common malicious patterns
        patterns = [
            (br'<script', 'Potential script injection'),
            (br'<?php', 'PHP code detected'),
            (br'eval\(', 'Potential code evaluation'),
            (br'exec\(', 'Potential command execution'),
        ]
        
        for pattern, risk in patterns:
            if pattern in content.lower():
                risks.append(risk)

        # Check file extension risks
        ext = Path(filename).suffix.lower()
        if ext in SECURITY['forbidden_extensions']:
            risks.append(f"Forbidden file extension: {ext}")

        # Check entropy for potential encrypted/packed content
        entropy = self._calculate_entropy(content)
        if entropy > 7.5:  # High entropy threshold
            risks.append("High entropy - possible encrypted/packed content")

        return risks

class FileNameValidator:
    """Secure filename validation and sanitization."""

    def __init__(self):
        """Initialize the filename validator."""
        self.forbidden_chars_regex = re.compile(f'[{re.escape(SECURITY["forbidden_chars"])}]')
        self.max_length = SECURITY['max_filename_length']

    def validate_filename(self, filename: str) -> ValidationResult:
        """Validate and sanitize a filename.
        
        Args:
            filename: Filename to validate
            
        Returns:
            ValidationResult: Validation result with sanitized filename
        """
        if not filename:
            return ValidationResult(
                is_valid=False,
                message="Empty filename",
                details={},
                validation_type="filename"
            )

        # Check length
        if len(filename) > self.max_length:
            return ValidationResult(
                is_valid=False,
                message=f"Filename too long (max {self.max_length} characters)",
                details={'length': len(filename)},
                validation_type="filename"
            )

        # Check forbidden characters
        if self.forbidden_chars_regex.search(filename):
            return ValidationResult(
                is_valid=False,
                message="Filename contains forbidden characters",
                details={'forbidden_chars': SECURITY['forbidden_chars']},
                risk_level="medium",
                validation_type="filename"
            )

        # Generate safe filename
        safe_name = self.sanitize_filename(filename)
        
        return ValidationResult(
            is_valid=True,
            message="Valid filename",
            details={'sanitized_name': safe_name},
            validation_type="filename"
        )

    def sanitize_filename(self, filename: str) -> str:
        """Create a safe version of the filename.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove forbidden characters
        safe_name = self.forbidden_chars_regex.sub('', filename)
        
        # Ensure safe length
        name, ext = os.path.splitext(safe_name)
        if len(safe_name) > self.max_length:
            name = name[:(self.max_length - len(ext) - 1)]
            safe_name = f"{name}{ext}"
            
        return safe_name
