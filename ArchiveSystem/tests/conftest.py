# -*- coding: utf-8 -*-
"""
Test Configuration
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import AppConfig
from database.db_manager import DatabaseManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration"""
    config = AppConfig()
    config.data_dir = temp_dir
    config.logs_dir = temp_dir / "logs"
    config.backups_dir = temp_dir / "backups"
    return config


@pytest.fixture
def test_db(test_config):
    """Create test database"""
    db = DatabaseManager(test_config)
    db.initialize()
    yield db
    db.close()
