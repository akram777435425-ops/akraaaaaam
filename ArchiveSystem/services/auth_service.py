# -*- coding: utf-8 -*-
"""
Authentication Service - Handles user authentication and authorization
الخدمة الأمنية - المصادقة والتفويض
"""

import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AuthService:
    """
    Professional authentication service with security features
    خدمة مصادقة احترافية مع ميزات أمنية
    """
    
    def __init__(self, db_manager, config):
        """Initialize authentication service"""
        self.db = db_manager
        self.config = config
        self.current_user = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using PBKDF2
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${hash_obj.hex()}"
    
    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hash_value: Password hash
        
        Returns:
            bool: True if password matches
        """
        try:
            salt, _ = hash_value.split('$')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return hmac.compare_digest(hash_obj.hex(), hash_value.split('$')[1])
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            # Get user from database
            query = "SELECT * FROM users WHERE username = ?"
            user = self.db.execute_one(query, (username,))
            
            if not user:
                logger.warning(f"Login attempt with non-existent user: {username}")
                return False, "Invalid username or password"
            
            # Check if user is locked
            if user['locked_until']:
                locked_until = datetime.fromisoformat(user['locked_until'])
                if datetime.now() < locked_until:
                    remaining = (locked_until - datetime.now()).total_seconds() / 60
                    return False, f"Account locked. Try again in {int(remaining)} minutes"
            
            # Check if user is active
            if not user['is_active']:
                logger.warning(f"Login attempt by inactive user: {username}")
                return False, "Account is inactive"
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                # Increment login attempts
                attempts = user['login_attempts'] + 1
                locked_until = None
                
                if attempts >= self.config.security.max_login_attempts:
                    locked_until = (datetime.now() + timedelta(
                        seconds=self.config.security.lockout_duration
                    )).isoformat()
                    logger.warning(f"Account locked due to failed login attempts: {username}")
                
                update_data = {'login_attempts': attempts}
                if locked_until:
                    update_data['locked_until'] = locked_until
                
                self.db.update('users', update_data, 'id = ?', (user['id'],))
                return False, "Invalid username or password"
            
            # Reset login attempts
            self.db.update('users', {
                'login_attempts': 0,
                'locked_until': None,
                'last_login': datetime.now().isoformat()
            }, 'id = ?', (user['id'],))
            
            self.current_user = dict(user)
            logger.info(f"User authenticated successfully: {username}")
            return True, "Authentication successful"
        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return False, "Authentication error occurred"
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str) -> Tuple[bool, str]:
        """
        Register new user
        
        Args:
            username: Username
            email: Email address
            password: Password
            full_name: Full name
        
        Returns:
            Tuple[bool, str]: (Success, Message)
        """
        try:
            # Validate password strength
            if len(password) < self.config.security.password_min_length:
                return False, f"Password must be at least {self.config.security.password_min_length} characters"
            
            # Check if user exists
            query = "SELECT id FROM users WHERE username = ? OR email = ?"
            if self.db.execute_one(query, (username, email)):
                return False, "Username or email already exists"
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'role': 'user',
                'is_active': True
            }
            
            user_id = self.db.insert('users', user_data)
            if user_id:
                logger.info(f"New user registered: {username}")
                return True, "User registered successfully"
            else:
                return False, "Failed to register user"
        
        except Exception as e:
            logger.error(f"User registration error: {str(e)}", exc_info=True)
            return False, "Registration error occurred"
    
    def logout(self) -> bool:
        """
        Logout current user
        
        Returns:
            bool: True if logout successful
        """
        try:
            if self.current_user:
                logger.info(f"User logged out: {self.current_user['username']}")
                self.current_user = None
                return True
            return False
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False
    
    def get_current_user(self):
        """Get current authenticated user"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has permission
        
        Args:
            permission: Permission to check
        
        Returns:
            bool: True if user has permission
        """
        if not self.current_user:
            return False
        
        role = self.current_user.get('role', 'user')
        
        # Admin has all permissions
        if role == 'admin':
            return True
        
        # Role-based permissions
        permissions = {
            'admin': ['view', 'create', 'edit', 'delete', 'manage_users', 'manage_backups'],
            'manager': ['view', 'create', 'edit', 'delete'],
            'user': ['view', 'create']
        }
        
        return permission in permissions.get(role, [])
