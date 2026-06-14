# -*- coding: utf-8 -*-
"""Database models for Archive System"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """User model"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    full_name: str = ""
    role: str = "user"  # admin, manager, user
    is_active: bool = True
    is_2fa_enabled: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None


@dataclass
class Document:
    """Document model"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    file_path: str = ""
    file_size: int = 0
    file_type: str = ""
    category_id: Optional[int] = None
    owner_id: int = 0
    is_archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    access_level: str = "private"  # private, shared, public
    tags: str = ""
    checksum: str = ""


@dataclass
class Category:
    """Category model"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    icon: str = ""
    color: str = "#000000"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ArchiveJob:
    """Archive job model"""
    id: Optional[int] = None
    job_name: str = ""
    document_id: int = 0
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0  # 0-100
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""


@dataclass
class BackupRecord:
    """Backup record model"""
    id: Optional[int] = None
    backup_name: str = ""
    backup_path: str = ""
    backup_size: int = 0
    status: str = "pending"  # pending, completed, failed
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    retention_days: int = 30


@dataclass
class AuditLog:
    """Audit log model"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: str = ""
    entity_type: str = ""
    entity_id: Optional[int] = None
    old_value: str = ""
    new_value: str = ""
    ip_address: str = ""
    user_agent: str = ""
    created_at: Optional[datetime] = None


@dataclass
class AccessControl:
    """Access control model"""
    id: Optional[int] = None
    user_id: int = 0
    document_id: int = 0
    permission_level: str = "view"  # view, edit, delete, admin
    granted_at: Optional[datetime] = None
    granted_by: Optional[int] = None
