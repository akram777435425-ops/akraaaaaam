# -*- coding: utf-8 -*-
"""
Common Utilities - Helper functions
الأدوات العامة - دوال مساعدة
"""

import logging
from typing import Optional, Any, List, Dict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class CommonUtils:
    """
    Common utility functions
    وظائف مشتركة
    """
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format bytes to human-readable size
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format datetime
        
        Args:
            dt: Datetime object
            format_str: Format string
        
        Returns:
            Formatted datetime string
        """
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime(format_str)
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """
        Get relative time string (e.g., "2 hours ago")
        
        Args:
            dt: Datetime object
        
        Returns:
            Relative time string
        """
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            weeks = int(seconds // 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 100) -> str:
        """
        Truncate string with ellipsis
        
        Args:
            text: Text to truncate
            max_length: Maximum length
        
        Returns:
            Truncated string
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def serialize_to_json(obj: Any) -> str:
        """
        Serialize object to JSON string
        
        Args:
            obj: Object to serialize
        
        Returns:
            JSON string
        """
        try:
            return json.dumps(obj, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            return "{}"
    
    @staticmethod
    def deserialize_from_json(json_str: str) -> Any:
        """
        Deserialize JSON string to object
        
        Args:
            json_str: JSON string
        
        Returns:
            Deserialized object
        """
        try:
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            return None
    
    @staticmethod
    def batch_list(items: List, batch_size: int) -> List[List]:
        """
        Split list into batches
        
        Args:
            items: List to split
            batch_size: Size of each batch
        
        Returns:
            List of batches
        """
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
    
    @staticmethod
    def merge_dicts(dict1: Dict, dict2: Dict, recursive: bool = True) -> Dict:
        """
        Merge two dictionaries
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            recursive: Whether to merge recursively
        
        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if recursive and isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = CommonUtils.merge_dicts(result[key], value, recursive)
            else:
                result[key] = value
        
        return result
