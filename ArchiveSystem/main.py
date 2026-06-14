#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archive System - Main Entry Point
تطبيق نظام إدارة الأرشيف الاحترافي
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import AppConfig
from ui.main_window import MainWindow
from logs.log_manager import LogManager
from database.db_manager import DatabaseManager

# Initialize logging
log_manager = LogManager()
logger = logging.getLogger(__name__)


def main():
    """
    Main application entry point
    نقطة دخول التطبيق الرئيسية
    """
    try:
        logger.info("Starting Archive System Application...")
        logger.info("بدء تشغيل تطبيق نظام إدارة الأرشيف...")
        
        # Initialize application configuration
        config = AppConfig()
        config.load_settings()
        logger.info(f"Configuration loaded: {config.app_name} v{config.version}")
        
        # Initialize database
        db = DatabaseManager(config)
        if not db.initialize():
            logger.error("Failed to initialize database")
            return 1
        logger.info("Database initialized successfully")
        
        # Launch UI
        app = MainWindow(config, db)
        app.run()
        
        logger.info("Archive System Application closed successfully")
        return 0
        
    except Exception as e:
        logger.critical(f"Fatal error in main application: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
