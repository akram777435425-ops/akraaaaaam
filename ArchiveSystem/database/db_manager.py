# -*- coding: utf-8 -*-
"""
Database Manager - Handles all database operations
مدير قاعدة البيانات - يتعامل مع جميع عمليات قاعدة البيانات
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Professional database manager with connection pooling and transaction support
    مدير قاعدة بيانات احترافي مع دعم تجمع الاتصالات والمعاملات
    """
    
    def __init__(self, config):
        """Initialize database manager"""
        self.config = config
        self.db_path = config.data_dir / "archive_system.db"
        self.connection = None
        self.lock = threading.RLock()
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize database and create tables
        
        Returns:
            bool: True if initialization successful
        """
        try:
            with self.lock:
                logger.info(f"Initializing database at: {self.db_path}")
                
                # Create connection
                self.connection = sqlite3.connect(
                    str(self.db_path),
                    timeout=self.config.database.timeout,
                    check_same_thread=False
                )
                self.connection.row_factory = sqlite3.Row
                
                # Enable foreign keys
                self.connection.execute("PRAGMA foreign_keys = ON")
                
                # Create tables
                self._create_tables()
                self.initialized = True
                logger.info("Database initialized successfully")
                return True
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            return False
    
    def _create_tables(self) -> None:
        """
        Create database tables
        إنشاء جداول قاعدة البيانات
        """
        tables = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                is_2fa_enabled BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
            """,
            
            # Documents table
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                category_id INTEGER,
                owner_id INTEGER NOT NULL,
                is_archived BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived_at TIMESTAMP,
                access_level TEXT DEFAULT 'private',
                tags TEXT,
                checksum TEXT,
                FOREIGN KEY(owner_id) REFERENCES users(id),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
            """,
            
            # Categories table
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Archive Jobs table
            """
            CREATE TABLE IF NOT EXISTS archive_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT NOT NULL,
                document_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            )
            """,
            
            # Audit Log table
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """,
            
            # Backup Records table
            """
            CREATE TABLE IF NOT EXISTS backup_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                backup_size INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                retention_days INTEGER DEFAULT 30
            )
            """,
            
            # Access Control table
            """
            CREATE TABLE IF NOT EXISTS access_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                permission_level TEXT DEFAULT 'view',
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(document_id) REFERENCES documents(id),
                FOREIGN KEY(granted_by) REFERENCES users(id),
                UNIQUE(user_id, document_id)
            )
            """,
        ]
        
        for table_sql in tables:
            try:
                self.connection.execute(table_sql)
            except Exception as e:
                logger.warning(f"Error creating table: {str(e)}")
        
        self.connection.commit()
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor
        
        Yields:
            sqlite3.Cursor: Database cursor
        """
        cursor = None
        try:
            with self.lock:
                cursor = self.connection.cursor()
                yield cursor
                self.connection.commit()
        except Exception as e:
            if cursor:
                self.connection.rollback()
            logger.error(f"Database cursor error: {str(e)}", exc_info=True)
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute(self, query: str, params: tuple = ()) -> Optional[Any]:
        """
        Execute database query
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Query result or None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}", exc_info=True)
            return None
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """
        Execute query and return single row
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Single row or None
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}", exc_info=True)
            return None
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert record into table
        
        Args:
            table: Table name
            data: Dictionary of column names and values
        
        Returns:
            Last inserted row ID or None
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(data.values()))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Insert operation failed: {str(e)}", exc_info=True)
            return None
    
    def update(self, table: str, data: Dict[str, Any], where: str = "", 
               params: tuple = ()) -> bool:
        """
        Update records in table
        
        Args:
            table: Table name
            data: Dictionary of columns to update
            where: WHERE clause (without 'WHERE')
            params: WHERE clause parameters
        
        Returns:
            bool: True if successful
        """
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause}"
            
            if where:
                query += f" WHERE {where}"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, tuple(data.values()) + params)
                return True
        except Exception as e:
            logger.error(f"Update operation failed: {str(e)}", exc_info=True)
            return False
    
    def delete(self, table: str, where: str = "", params: tuple = ()) -> bool:
        """
        Delete records from table
        
        Args:
            table: Table name
            where: WHERE clause (without 'WHERE')
            params: WHERE clause parameters
        
        Returns:
            bool: True if successful
        """
        try:
            query = f"DELETE FROM {table}"
            if where:
                query += f" WHERE {where}"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return True
        except Exception as e:
            logger.error(f"Delete operation failed: {str(e)}", exc_info=True)
            return False
    
    def close(self) -> None:
        """Close database connection"""
        try:
            with self.lock:
                if self.connection:
                    self.connection.close()
                    self.initialized = False
                    logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")
    
    def __del__(self):
        """Destructor - ensure connection is closed"""
        self.close()
