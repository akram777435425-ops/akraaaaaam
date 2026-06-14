# -*- coding: utf-8 -*-
"""
Security Utilities - Encryption, validation, and security functions
أدوات الأمان - التشفير والبالتحقق
"""

import re
import logging
from typing import Optional, List
from urllib.parse import quote

logger = logging.getLogger(__name__)


class SecurityUtils:
    """
    Security utility functions
    وظائف أمان مفيدة
    """
    
    # Regular expressions for validation
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    USERNAME_REGEX = r'^[a-zA-Z0-9_-]{3,20}$'
    PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address
        
        Args:
            email: Email address to validate
        
        Returns:
            bool: True if valid email
        """
        if not email or len(email) > 254:
            return False
        return re.match(SecurityUtils.EMAIL_REGEX, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username
        
        Args:
            username: Username to validate
        
        Returns:
            bool: True if valid username
        """
        return re.match(SecurityUtils.USERNAME_REGEX, username) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple:
        """
        Validate password strength
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple[bool, str]: (Is valid, Message)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain digits")
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain special characters (@$!%*?&)")
        
        if errors:
            return False, " | ".join(errors)
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(user_input: str, max_length: int = 500) -> str:
        """
        Sanitize user input to prevent XSS attacks
        
        Args:
            user_input: User input to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized input
        """
        if not user_input:
            return ""
        
        # Limit length
        user_input = user_input[:max_length]
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            user_input = user_input.replace(char, '')
        
        return user_input.strip()
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path to prevent directory traversal
        
        Args:
            file_path: File path to validate
        
        Returns:
            bool: True if path is safe
        """
        # Check for directory traversal attempts
        if ".." in file_path or "//" in file_path:
            return False
        
        # Check for absolute paths (security consideration)
        if file_path.startswith('/'):
            return False
        
        return True
    
    @staticmethod
    def validate_sql_input(sql_input: str) -> bool:
        """
        Validate SQL input to detect injection attempts
        
        Args:
            sql_input: SQL input to validate
        
        Returns:
            bool: True if input seems safe
        """
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION',
                            'SELECT', 'EXEC', 'EXECUTE', 'SCRIPT']
        
        upper_input = sql_input.upper()
        for keyword in dangerous_keywords:
            if keyword in upper_input:
                return False
        
        return True
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate secure random token
        
        Args:
            length: Token length
        
        Returns:
            Random token
        """
        import secrets
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def escape_url(url: str) -> str:
        """
        Escape URL for safe output
        
        Args:
            url: URL to escape
        
        Returns:
            Escaped URL
        """
        return quote(url, safe=':/?#[]@!$&\'()*+,;=')
