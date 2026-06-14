# -*- coding: utf-8 -*-
"""
Audit Service - Handles audit logging and tracking
خدمة التدقيق - تسجيل وتتبع العمليات
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AuditService:
    """
    Professional audit service for tracking all system activities
    خدمة تدقيق احترافية لتتبع تشاطات النظام 
    """
    
    def __init__(self, db_manager):
        """Initialize audit service"""
        self.db = db_manager
    
    def log_action(self, user_id: Optional[int], action: str, entity_type: str,
                  entity_id: Optional[int], old_value: str = "",
                  new_value: str = "", ip_address: str = "",
                  user_agent: str = "") -> Optional[int]:
        """
        Log system action
        
        Args:
            user_id: User ID performing action
            action: Action type (create, read, update, delete)
            entity_type: Type of entity (user, document, backup)
            entity_id: ID of entity
            old_value: Previous value (for updates)
            new_value: New value (for updates)
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Log record ID if successful
        """
        try:
            audit_data = {
                'user_id': user_id,
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'old_value': old_value,
                'new_value': new_value,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            
            log_id = self.db.insert('audit_log', audit_data)
            if log_id:
                logger.debug(f"Audit log created: {action} on {entity_type} by user {user_id}")
            
            return log_id
        
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}", exc_info=True)
            return None
    
    def get_audit_log(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Get audit log entry
        
        Args:
            log_id: Log entry ID
        
        Returns:
            Log entry data or None
        """
        try:
            query = "SELECT * FROM audit_log WHERE id = ?"
            result = self.db.execute_one(query, (log_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Get audit log error: {str(e)}")
            return None
    
    def get_user_actions(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get user's recent actions
        
        Args:
            user_id: User ID
            limit: Maximum number of records
        
        Returns:
            List of audit log entries
        """
        try:
            query = "SELECT * FROM audit_log WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
            results = self.db.execute(query, (user_id, limit))
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Get user actions error: {str(e)}")
            return []
    
    def get_entity_history(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """
        Get history of entity changes
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
        
        Returns:
            List of audit log entries
        """
        try:
            query = "SELECT * FROM audit_log WHERE entity_type = ? AND entity_id = ? ORDER BY created_at DESC"
            results = self.db.execute(query, (entity_type, entity_id))
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Get entity history error: {str(e)}")
            return []
    
    def search_audit_logs(self, action: str = "", entity_type: str = "",
                         user_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search audit logs with filters
        
        Args:
            action: Filter by action type
            entity_type: Filter by entity type
            user_id: Filter by user ID
            limit: Maximum number of records
        
        Returns:
            List of matching audit log entries
        """
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if action:
                query += " AND action = ?"
                params.append(action)
            
            if entity_type:
                query += " AND entity_type = ?"
                params.append(entity_type)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db.execute(query, tuple(params))
            return [dict(row) for row in results] if results else []
        
        except Exception as e:
            logger.error(f"Search audit logs error: {str(e)}")
            return []
