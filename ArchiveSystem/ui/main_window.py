# -*- coding: utf-8 -*-
"""
Main Window - Application main UI window
النافذة الرئيسية - نافذة واجهة الاستخدام
"""

import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main application window
    نافذة التطبيق الرئيسية
    """
    
    def __init__(self, config, db_manager):
        """Initialize main window"""
        self.config = config
        self.db = db_manager
        self.root = tk.Tk()
        self.root.title(f"{config.app_name} v{config.version}")
        self.root.geometry(f"{config.ui.window_width}x{config.ui.window_height}")
        
        logger.info("Main window initialized")
    
    def run(self) -> None:
        """
        Run the application main loop
        تشغيل حلقة التطبيق الرئيسية
        """
        try:
            logger.info("Starting main application loop")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Application error: {str(e)}")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """
        Cleanup resources before exit
        بتنظيف الموارد قبل الإغلاق
        """
        try:
            if self.db:
                self.db.close()
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
