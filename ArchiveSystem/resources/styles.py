# -*- coding: utf-8 -*-
"""
Application Styles - CSS/QSS style definitions
أنماط التطبيق - تعريفات الأنماط
"""

# Modern Dark Theme
MODERN_DARK = """
* {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: Arial, sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #2d2d2d;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #0d5a9e;
}

QLineEdit, QTextEdit {
    background-color: #3d3d3d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    color: #e0e0e0;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #0078d4;
}

QTableWidget {
    background-color: #2d2d2d;
    gridline-color: #444444;
}

QHeaderView::section {
    background-color: #3d3d3d;
    padding: 5px;
    border: none;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #444444;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #444444;
}

QMenu::item:selected {
    background-color: #0078d4;
}
"""

# Light Theme
LIGHT_THEME = """
* {
    background-color: #ffffff;
    color: #333333;
    font-family: Arial, sans-serif;
    font-size: 10pt;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 15px;
}

QPushButton:hover {
    background-color: #106ebe;
}
"""

# Get styles
STYLES = {
    'modern_dark': MODERN_DARK,
    'light': LIGHT_THEME
}


def get_style(theme_name: str = 'modern_dark') -> str:
    """
    Get style sheet for theme
    
    Args:
        theme_name: Theme name
    
    Returns:
        Style sheet string
    """
    return STYLES.get(theme_name, MODERN_DARK)
