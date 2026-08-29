from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QListWidget, QListWidgetItem, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
import logging

logger = logging.getLogger(__name__)


class DependencyDialog(QDialog):
    """Dialog for checking and installing dependencies."""
    
    def __init__(self, parent=None):
        """Initialize dependency dialog."""
        super().__init__(parent)
        self.setWindowTitle("Check Dependencies")
        self.setGeometry(200, 200, 600, 500)
        self._setup_ui()
        self._check_dependencies()
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Checking project dependencies..."))
        
        # Dependency list
        self.dep_list = QListWidget()
        layout.addWidget(self.dep_list)
        
        # Status
        self.status_label = QLabel("Checking...")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        install_btn = QPushButton("Install Missing")
        install_btn.clicked.connect(self.install_dependencies)
        button_layout.addWidget(install_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _check_dependencies(self):
        """Check all dependencies."""
        from src.core.dependency_checker import DependencyChecker
        
        checker = DependencyChecker()
        python_status, system_status, all_good = checker.check_all()
        
        # Python packages
        self.dep_list.addItem(QListWidgetItem("Python Packages:"))
        for package, status in python_status.items():
            item = QListWidgetItem(f"  {package}: {'✓' if status else '✗'}")
            if not status:
                item.setForeground(QColor(255, 0, 0))
            self.dep_list.addItem(item)
        
        # System dependencies
        self.dep_list.addItem(QListWidgetItem("\nSystem Dependencies:"))
        for tool, status in system_status.items():
            item = QListWidgetItem(f"  {tool}: {'✓' if status else '✗'}")
            if not status:
                item.setForeground(QColor(255, 0, 0))
            self.dep_list.addItem(item)
        
        # Status
        if all_good:
            self.status_label.setText("✓ All dependencies are installed")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("✗ Some dependencies are missing")
            self.status_label.setStyleSheet("color: red;")
    
    def install_dependencies(self):
        """Install missing dependencies."""
        from src.core.dependency_checker import DependencyChecker
        
        checker = DependencyChecker()
        
        logger.info("Installing Python packages...")
        if checker.install_python_packages():
            logger.info("Python packages installed successfully")
        
        self.status_label.setText("Installation complete. Please check the output above.")


class DATDownloadDialog(QDialog):
    """Dialog for downloading DAT files."""
    
    def __init__(self, parent=None):
        """Initialize DAT download dialog."""
        super().__init__(parent)
        self.setWindowTitle("Download DAT Files")
        self.setGeometry(200, 200, 600, 400)
        self._setup_ui()
        self._load_systems()
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        
        # DAT collection selector
        collection_layout = QHBoxLayout()
        collection_layout.addWidget(QLabel("DAT Collection:"))
        
        self.collection_combo = QComboBox()
        self.collection_combo.addItems(["No-Intro", "Redump", "TOSEC"])
        self.collection_combo.currentTextChanged.connect(self._on_collection_changed)
        collection_layout.addWidget(self.collection_combo)
        collection_layout.addStretch()
        
        layout.addLayout(collection_layout)
        
        # Systems list
        layout.addWidget(QLabel("Select systems to download:"))
        
        self.systems_list = QListWidget()
        layout.addWidget(self.systems_list)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Download Selected")
        download_btn.clicked.connect(self.download_selected)
        button_layout.addWidget(download_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_systems(self):
        """Load available systems from Libretro."""
        from src.core.libretro_integration import LibretroMetadataManager
        
        manager = LibretroMetadataManager()
        
        # Check if cache is valid, otherwise refresh
        if not manager.is_cache_valid():
            logger.info("Refreshing systems from Libretro...")
            manager.refresh_all_systems()
        
        self._populate_systems_list()
    
    def _populate_systems_list(self):
        """Populate systems list."""
        from src.core.libretro_integration import LibretroMetadataManager
        
        manager = LibretroMetadataManager()
        collection = self.collection_combo.currentText()
        systems = manager.get_systems_by_collection(collection)
        
        self.systems_list.clear()
        for system_name in sorted(systems.keys()):
            item = QListWidgetItem(system_name)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.systems_list.addItem(item)
    
    def _on_collection_changed(self):
        """Handle collection selection change."""
        self._populate_systems_list()
    
    def download_selected(self):
        """Download selected systems."""
        selected = []
        for i in range(self.systems_list.count()):
            item = self.systems_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        
        if not selected:
            logger.warning("No systems selected")
            return
        
        logger.info(f"Downloading DAT files for: {', '.join(selected)}")
        self.progress_bar.setVisible(True)
