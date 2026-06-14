# -*- coding: utf-8 -*-
"""
Document Service - Handles document operations
خدمة المستندات - تداول عمليات المستندات
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Professional document service with file operations
    خدمة مستندات احترافية مع عمليات الملفات
    """
    
    def __init__(self, db_manager, config):
        """Initialize document service"""
        self.db = db_manager
        self.config = config
        self.storage_dir = config.data_dir / "documents"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """
        Calculate file checksum
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 checksum
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation error: {str(e)}")
            return ""
    
    def upload_document(self, file_path: str, title: str, description: str,
                       category_id: Optional[int], owner_id: int,
                       access_level: str = "private") -> Optional[int]:
        """
        Upload document to system
        
        Args:
            file_path: Source file path
            title: Document title
            description: Document description
            category_id: Category ID
            owner_id: Owner user ID
            access_level: Access level (private, shared, public)
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            source_file = Path(file_path)
            if not source_file.exists():
                logger.error(f"Source file not found: {file_path}")
                return None
            
            # Generate storage path
            file_name = source_file.name
            stored_path = self.storage_dir / f"{owner_id}_{datetime.now().timestamp()}_{file_name}"
            
            # Copy file to storage
            with open(source_file, 'rb') as src:
                with open(stored_path, 'wb') as dst:
                    dst.write(src.read())
            
            # Calculate checksum
            checksum = self.calculate_checksum(str(stored_path))
            
            # Get file info
            file_size = stored_path.stat().st_size
            file_type = source_file.suffix.lower()
            
            # Create document record
            doc_data = {
                'title': title,
                'description': description,
                'file_path': str(stored_path),
                'file_size': file_size,
                'file_type': file_type,
                'category_id': category_id,
                'owner_id': owner_id,
                'access_level': access_level,
                'checksum': checksum
            }
            
            doc_id = self.db.insert('documents', doc_data)
            if doc_id:
                logger.info(f"Document uploaded successfully: {title} (ID: {doc_id})")
                return doc_id
            else:
                # Delete file if database insertion failed
                stored_path.unlink()
                return None
        
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}", exc_info=True)
            return None
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get document by ID
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document data or None
        """
        try:
            query = "SELECT * FROM documents WHERE id = ?"
            result = self.db.execute_one(query, (doc_id,))
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Get document error: {str(e)}")
            return None
    
    def list_documents(self, owner_id: int, category_id: Optional[int] = None,
                      search_query: str = "") -> List[Dict[str, Any]]:
        """
        List documents with filtering
        
        Args:
            owner_id: Owner user ID
            category_id: Optional category filter
            search_query: Optional search query
        
        Returns:
            List of documents
        """
        try:
            query = "SELECT * FROM documents WHERE owner_id = ?"
            params = [owner_id]
            
            if category_id:
                query += " AND category_id = ?"
                params.append(category_id)
            
            if search_query:
                query += " AND (title LIKE ? OR description LIKE ?"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
                query += ")"
            
            query += " ORDER BY created_at DESC"
            
            results = self.db.execute(query, tuple(params))
            return [dict(row) for row in results] if results else []
        
        except Exception as e:
            logger.error(f"List documents error: {str(e)}")
            return []
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete document
        
        Args:
            doc_id: Document ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Get document
            doc = self.get_document(doc_id)
            if not doc:
                return False
            
            # Delete file
            file_path = Path(doc['file_path'])
            if file_path.exists():
                file_path.unlink()
            
            # Delete database record
            return self.db.delete('documents', 'id = ?', (doc_id,))
        
        except Exception as e:
            logger.error(f"Delete document error: {str(e)}")
            return False
    
    def archive_document(self, doc_id: int) -> bool:
        """
        Archive document
        
        Args:
            doc_id: Document ID
        
        Returns:
            bool: True if successful
        """
        try:
            return self.db.update('documents', {
                'is_archived': True,
                'archived_at': datetime.now().isoformat()
            }, 'id = ?', (doc_id,))
        except Exception as e:
            logger.error(f"Archive document error: {str(e)}")
            return False
    
    def restore_document(self, doc_id: int) -> bool:
        """
        Restore archived document
        
        Args:
            doc_id: Document ID
        
        Returns:
            bool: True if successful
        """
        try:
            return self.db.update('documents', {
                'is_archived': False,
                'archived_at': None
            }, 'id = ?', (doc_id,))
        except Exception as e:
            logger.error(f"Restore document error: {str(e)}")
            return False
