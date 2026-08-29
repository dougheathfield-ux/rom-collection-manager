from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QProgressBar, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("ROM Collection Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_menu_bar()
        self._setup_ui()
        self._setup_status_bar()
        
        logger.info("Main window initialized")
    
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = file_menu.addAction("&Open Directory")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_directory)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        check_deps_action = tools_menu.addAction("Check &Dependencies")
        check_deps_action.triggered.connect(self.on_check_dependencies)
        
        download_dat_action = tools_menu.addAction("Download &DAT Files")
        download_dat_action.triggered.connect(self.on_download_dat)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.on_about)
    
    def _setup_ui(self):
        """Setup main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Import from local files tab
        from src.gui.tabs import LocalFilesTab, ArchiveTab, ResultsTab
        
        self.local_files_tab = LocalFilesTab()
        self.archive_tab = ArchiveTab()
        self.results_tab = ResultsTab()
        
        tabs.addTab(self.local_files_tab, "Local Files")
        tabs.addTab(self.archive_tab, "Archives")
        tabs.addTab(self.results_tab, "Results")
        
        layout.addWidget(tabs)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        central_widget.setLayout(layout)
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
    
    def on_open_directory(self):
        """Handle open directory action."""
        from PyQt6.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.local_files_tab.scan_directory(directory)
            self.status_label.setText(f"Scanned: {directory}")
    
    def on_check_dependencies(self):
        """Handle check dependencies action."""
        from src.gui.dialogs import DependencyDialog
        
        dialog = DependencyDialog(self)
        dialog.exec()
    
    def on_download_dat(self):
        """Handle download DAT files action."""
        from src.gui.dialogs import DATDownloadDialog
        
        dialog = DATDownloadDialog(self)
        dialog.exec()
    
    def on_about(self):
        """Handle about action."""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About ROM Collection Manager",
            "ROM Collection Manager v0.1.0\n\n"
            "Manage, validate, and organize ROM collections using No-Intro and Redump databases.\n\n"
            "© 2026 dougheathfield-ux"
        )
    
    def update_progress(self, current: int, total: int):
        """Update progress bar."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_bar.setVisible(True)
        
        if current >= total:
            self.progress_bar.setVisible(False)
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_label.setText(message)
