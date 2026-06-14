# -*- coding: utf-8 -*-
"""
Logging Manager - Professional logging configuration
مدير السجلات - إعدادات التسجيل الاحترافية
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


class LogManager:
    """
    Professional log manager with rotating file handlers
    مدير سجلات احترافي مع معالجات ملفات دورانة
    """
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, logs_dir: Path = None):
        """Initialize log manager"""
        self.logs_dir = logs_dir or Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        Setup logging configuration
        إعداد تكوين التسجيل
        """
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler - All logs (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "archive_system.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # File handler - Errors only
        error_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # File handler - Audit logs
        audit_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "audit.log",
            maxBytes=20 * 1024 * 1024,  # 20 MB
            backupCount=10
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(detailed_formatter)
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
        
        logging.info("Logging system initialized")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get logger instance
        
        Args:
            name: Logger name (usually __name__)
        
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def set_level(level: int) -> None:
        """
        Set logging level
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(level)
