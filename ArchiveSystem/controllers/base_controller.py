# -*- coding: utf-8 -*-
"""
Base Controller - Base class for all controllers
التحكم الأساسي - الفئة الأساسية لجميع المتحكمات
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BaseController:
    """
    Base controller class with common functionality
    فئة التحكم الأساسية مع الوظائف المشتركة
    """
    
    def __init__(self, auth_service, db_manager, config):
        """Initialize base controller"""
        self.auth = auth_service
        self.db = db_manager
        self.config = config
    
    def require_auth(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated
        """
        if not self.auth.is_authenticated():
            logger.warning("Access denied: User not authenticated")
            return False
        return True
    
    def require_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            permission: Permission to check
        
        Returns:
            bool: True if user has permission
        """
        if not self.require_auth():
            return False
        
        if not self.auth.has_permission(permission):
            logger.warning(f"Access denied: Missing permission {permission}")
            return False
        
        return True
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user
        
        Returns:
            Current user or None
        """
        return self.auth.get_current_user()
    
    def success_response(self, message: str = "", data: Any = None) -> Dict[str, Any]:
        """
        Create success response
        
        Args:
            message: Success message
            data: Response data
        
        Returns:
            Response dictionary
        """
        return {
            'success': True,
            'message': message,
            'data': data
        }
    
    def error_response(self, message: str = "", error_code: str = "ERROR") -> Dict[str, Any]:
        """
        Create error response
        
        Args:
            message: Error message
            error_code: Error code
        
        Returns:
            Response dictionary
        """
        return {
            'success': False,
            'message': message,
            'error_code': error_code,
            'data': None
        }
