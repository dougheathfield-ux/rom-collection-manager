#!/usr/bin/env python3
"""
ROM Collection Manager - Main Application Entry Point

A comprehensive GUI application for managing ROM collections with CRC validation,
metadata synchronization with Libretro, and archive handling for No-Intro and Redump
databases.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """
    Main application entry point.
    """
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("ROM Collection Manager")
        app.setApplicationVersion("0.1.0")
        
        # Import and show main window
        from src.gui.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        logger.info("Application started")
        
        # Run application
        sys.exit(app.exec())
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
