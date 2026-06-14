# -*- coding: utf-8 -*-
"""
Backup Service - Handles backup and restore operations
خدمة النسخاتالاحتياطية - النسخو والاستعادة
"""

import os
import shutil
import logging
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BackupService:
    """
    Professional backup service with compression and scheduling
    خدمة نسخاتاحتياطية احترافية مع الضغط والجدولة
    """
    
    def __init__(self, db_manager, config):
        """Initialize backup service"""
        self.db = db_manager
        self.config = config
        self.backups_dir = config.backups_dir
        self.backups_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, backup_name: str, retention_days: int = 30) -> Optional[int]:
        """
        Create system backup
        
        Args:
            backup_name: Name for backup
            retention_days: Number of days to retain backup
        
        Returns:
            Backup record ID if successful, None otherwise
        """
        try:
            logger.info(f"Starting backup: {backup_name}")
            
            # Create backup file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_name}_{timestamp}.zip"
            backup_path = self.backups_dir / backup_filename
            
            # Create backup record
            backup_data = {
                'backup_name': backup_name,
                'backup_path': str(backup_path),
                'status': 'running',
                'retention_days': retention_days
            }
            
            backup_id = self.db.insert('backup_records', backup_data)
            if not backup_id:
                return None
            
            # Create backup zip file
            try:
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Backup documents
                    docs_dir = self.config.data_dir / "documents"
                    if docs_dir.exists():
                        for file_path in docs_dir.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.config.data_dir)
                                zipf.write(file_path, arcname)
                    
                    # Backup database
                    if (self.config.data_dir / "archive_system.db").exists():
                        zipf.write(
                            self.config.data_dir / "archive_system.db",
                            "archive_system.db"
                        )
                
                # Get backup size
                backup_size = backup_path.stat().st_size
                
                # Update backup record
                self.db.update('backup_records', {
                    'status': 'completed',
                    'backup_size': backup_size,
                    'completed_at': datetime.now().isoformat()
                }, 'id = ?', (backup_id,))
                
                logger.info(f"Backup completed successfully: {backup_name} ({backup_size} bytes)")
                return backup_id
            
            except Exception as e:
                logger.error(f"Backup creation error: {str(e)}", exc_info=True)
                self.db.update('backup_records', {
                    'status': 'failed',
                    'error_message': str(e)
                }, 'id = ?', (backup_id,))
                return None
        
        except Exception as e:
            logger.error(f"Backup initialization error: {str(e)}", exc_info=True)
            return None
    
    def restore_backup(self, backup_id: int) -> bool:
        """
        Restore from backup
        
        Args:
            backup_id: Backup record ID
        
        Returns:
            bool: True if restoration successful
        """
        try:
            logger.info(f"Starting restoration from backup ID: {backup_id}")
            
            # Get backup record
            query = "SELECT * FROM backup_records WHERE id = ?"
            backup = self.db.execute_one(query, (backup_id,))
            
            if not backup:
                logger.error(f"Backup record not found: {backup_id}")
                return False
            
            backup_path = Path(backup['backup_path'])
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create restore point
            restore_dir = self.backups_dir / f"restore_{datetime.now().timestamp()}"
            restore_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # Extract backup
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(restore_dir)
                
                # Copy restored files back
                # Note: In production, implement more careful restoration logic
                logger.info(f"Backup restored to: {restore_dir}")
                return True
            
            except Exception as e:
                logger.error(f"Backup restoration error: {str(e)}", exc_info=True)
                return False
        
        except Exception as e:
            logger.error(f"Restoration initialization error: {str(e)}", exc_info=True)
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy
        
        Returns:
            Number of backups deleted
        """
        try:
            deleted_count = 0
            now = datetime.now()
            
            # Get all backups from database
            query = "SELECT * FROM backup_records WHERE status = 'completed'"
            backups = self.db.execute(query)
            
            if not backups:
                return 0
            
            for backup in backups:
                created_at = datetime.fromisoformat(backup['created_at'])
                retention_days = backup['retention_days']
                
                if (now - created_at).days > retention_days:
                    # Delete backup file
                    backup_path = Path(backup['backup_path'])
                    if backup_path.exists():
                        backup_path.unlink()
                        logger.info(f"Deleted old backup: {backup_path}")
                    
                    # Delete database record
                    self.db.delete('backup_records', 'id = ?', (backup['id'],))
                    deleted_count += 1
            
            logger.info(f"Cleanup completed: {deleted_count} old backups deleted")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Backup cleanup error: {str(e)}", exc_info=True)
            return 0
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all backups
        
        Returns:
            List of backup records
        """
        try:
            query = "SELECT * FROM backup_records ORDER BY created_at DESC"
            results = self.db.execute(query)
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"List backups error: {str(e)}")
            return []
