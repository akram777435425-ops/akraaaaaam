# -*- coding: utf-8 -*-
"""
Validation Utilities - Input validation and data checking
أدوات البالتحقق - البالتحقق من المدخلات
"""

import os
import logging
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationUtils:
    """
    Validation utility functions
    وظائف بالتحقق مفيدة
    """
    
    # File size limits
    MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
    MAX_BACKUP_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.txt', '.csv', '.zip',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp'
    ]
    
    @staticmethod
    def validate_file_size(file_path: str, max_size: int = None) -> bool:
        """
        Validate file size
        
        Args:
            file_path: Path to file
            max_size: Maximum allowed size in bytes
        
        Returns:
            bool: True if file size is valid
        """
        if max_size is None:
            max_size = ValidationUtils.MAX_UPLOAD_SIZE
        
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= max_size
        except Exception as e:
            logger.error(f"File size validation error: {str(e)}")
            return False
    
    @staticmethod
    def validate_file_extension(file_path: str, allowed_extensions: list = None) -> bool:
        """
        Validate file extension
        
        Args:
            file_path: Path to file
            allowed_extensions: List of allowed extensions
        
        Returns:
            bool: True if extension is allowed
        """
        if allowed_extensions is None:
            allowed_extensions = ValidationUtils.ALLOWED_EXTENSIONS
        
        ext = Path(file_path).suffix.lower()
        return ext in allowed_extensions
    
    @staticmethod
    def validate_file(file_path: str, max_size: int = None) -> bool:
        """
        Validate file (size and extension)
        
        Args:
            file_path: Path to file
            max_size: Maximum allowed size
        
        Returns:
            bool: True if file is valid
        """
        if not Path(file_path).exists():
            logger.warning(f"File does not exist: {file_path}")
            return False
        
        if not ValidationUtils.validate_file_extension(file_path):
            logger.warning(f"Invalid file extension: {file_path}")
            return False
        
        if not ValidationUtils.validate_file_size(file_path, max_size):
            logger.warning(f"File size exceeds limit: {file_path}")
            return False
        
        return True
    
    @staticmethod
    def validate_string(value: str, min_length: int = 1, max_length: int = 1000) -> bool:
        """
        Validate string length
        
        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length
        
        Returns:
            bool: True if valid
        """
        if not isinstance(value, str):
            return False
        return min_length <= len(value) <= max_length
    
    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> bool:
        """
        Validate integer
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        
        Returns:
            bool: True if valid
        """
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                return False
            
            if max_value is not None and int_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_choice(value: str, choices: list) -> bool:
        """
        Validate value is in allowed choices
        
        Args:
            value: Value to validate
            choices: List of allowed values
        
        Returns:
            bool: True if value is in choices
        """
        return value in choices
