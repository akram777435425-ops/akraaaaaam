# -*- coding: utf-8 -*-
"""
Application Settings and Configuration
إعدادات وتكوين التطبيق
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: str = "sqlite"  # sqlite, mysql, postgresql
    host: str = "localhost"
    port: int = 5432
    database: str = "archive_system"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    timeout: int = 30


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_encryption: bool = True
    enable_2fa: bool = True
    password_min_length: int = 8
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes


@dataclass
class UIConfig:
    """UI configuration"""
    theme: str = "modern_dark"
    language: str = "ar"  # Arabic
    font_family: str = "Arial"
    font_size: int = 10
    window_width: int = 1280
    window_height: int = 800
    enable_animations: bool = True


class AppConfig:
    """
    Main application configuration class
    فئة التكوين الرئيسية للتطبيق
    """
    
    def __init__(self):
        """Initialize application configuration"""
        self.app_name = "Archive System"
        self.version = "1.0.0"
        self.description = "Professional Archive Management System"
        
        # Paths
        self.app_root = Path(__file__).parent.parent
        self.config_dir = self.app_root / "config"
        self.data_dir = self.app_root.parent / "data"
        self.logs_dir = self.app_root / "logs"
        self.backups_dir = self.data_dir / "backups"
        self.resources_dir = self.app_root / "resources"
        
        # Create necessary directories
        self._create_directories()
        
        # Configuration objects
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.ui = UIConfig()
        
        # Configuration file path
        self.config_file = self.config_dir / "config.json"
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        for directory in [self.config_dir, self.data_dir, self.logs_dir, 
                         self.backups_dir, self.resources_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self) -> bool:
        """
        Load settings from configuration file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Load database config
                if 'database' in config_data:
                    db_cfg = config_data['database']
                    self.database = DatabaseConfig(**db_cfg)
                
                # Load security config
                if 'security' in config_data:
                    sec_cfg = config_data['security']
                    self.security = SecurityConfig(**sec_cfg)
                
                # Load UI config
                if 'ui' in config_data:
                    ui_cfg = config_data['ui']
                    self.ui = UIConfig(**ui_cfg)
                
                return True
            else:
                # Create default config file
                self.save_settings()
                return True
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            return False
    
    def save_settings(self) -> bool:
        """
        Save settings to configuration file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            config_data = {
                'app_name': self.app_name,
                'version': self.version,
                'database': {
                    'db_type': self.database.db_type,
                    'host': self.database.host,
                    'port': self.database.port,
                    'database': self.database.database,
                    'pool_size': self.database.pool_size,
                    'timeout': self.database.timeout,
                },
                'security': {
                    'enable_encryption': self.security.enable_encryption,
                    'enable_2fa': self.security.enable_2fa,
                    'password_min_length': self.security.password_min_length,
                    'session_timeout': self.security.session_timeout,
                    'max_login_attempts': self.security.max_login_attempts,
                    'lockout_duration': self.security.lockout_duration,
                },
                'ui': {
                    'theme': self.ui.theme,
                    'language': self.ui.language,
                    'font_family': self.ui.font_family,
                    'font_size': self.ui.font_size,
                    'window_width': self.ui.window_width,
                    'window_height': self.ui.window_height,
                    'enable_animations': self.ui.enable_animations,
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        try:
            parts = key.split('.')
            value = None
            
            if parts[0] == 'database':
                value = self.database
            elif parts[0] == 'security':
                value = self.security
            elif parts[0] == 'ui':
                value = self.ui
            else:
                return getattr(self, parts[0], default)
            
            for part in parts[1:]:
                value = getattr(value, part)
            
            return value
        except (AttributeError, IndexError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dots)
            value: Value to set
        
        Returns:
            bool: True if set successfully
        """
        try:
            parts = key.split('.')
            
            if len(parts) == 1:
                setattr(self, parts[0], value)
            elif parts[0] == 'database':
                setattr(self.database, parts[1], value)
            elif parts[0] == 'security':
                setattr(self.security, parts[1], value)
            elif parts[0] == 'ui':
                setattr(self.ui, parts[1], value)
            else:
                return False
            
            return True
        except (AttributeError, IndexError):
            return False
