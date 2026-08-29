from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QSpinBox, QCheckBox, QComboBox, QGroupBox, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
import logging
import os

logger = logging.getLogger(__name__)


class LocalFilesTab(QWidget):
    """Tab for scanning and processing local ROM files."""
    
    files_scanned = pyqtSignal(list)  # List of file dicts
    
    def __init__(self):
        """Initialize local files tab."""
        super().__init__()
        self.scanned_files = []
        self.input_directory = ""
        self.output_directory = ""
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        
        # Input/Output folder selection group
        folder_group = QGroupBox("ROM Folder Configuration")
        folder_layout = QVBoxLayout()
        
        # Input folder
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input Folder (ROMs to scan):"))
        self.input_label = QLineEdit()
        self.input_label.setReadOnly(True)
        self.input_label.setPlaceholderText("No folder selected")
        input_layout.addWidget(self.input_label)
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(input_browse_btn)
        folder_layout.addLayout(input_layout)
        
        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder (Organized ROMs):"))
        self.output_label = QLineEdit()
        self.output_label.setReadOnly(True)
        self.output_label.setPlaceholderText("No folder selected")
        output_layout.addWidget(self.output_label)
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(output_browse_btn)
        folder_layout.addLayout(output_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Directory selection (legacy, kept for compatibility)
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        
        dir_layout.addWidget(QLabel("Quick Scan Directory:"))
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(browse_btn)
        dir_layout.addStretch()
        
        layout.addLayout(dir_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.recursive_check = QCheckBox("Scan Subdirectories")
        self.recursive_check.setChecked(True)
        options_layout.addWidget(self.recursive_check)
        
        options_layout.addStretch()
        
        scan_btn = QPushButton("Scan Directory")
        scan_btn.clicked.connect(self.on_scan_clicked)
        options_layout.addWidget(scan_btn)
        
        layout.addLayout(options_layout)
        
        # Files table
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(6)
        self.files_table.setHorizontalHeaderLabels([
            "Filename", "System", "Size", "CRC32", "Status", "Match"
        ])
        self.files_table.setColumnWidth(0, 250)
        self.files_table.setColumnWidth(1, 100)
        self.files_table.setColumnWidth(2, 100)
        self.files_table.setColumnWidth(3, 100)
        self.files_table.setColumnWidth(4, 100)
        self.files_table.setColumnWidth(5, 200)
        
        layout.addWidget(QLabel("ROM Files:"))
        layout.addWidget(self.files_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        calculate_crc_btn = QPushButton("Calculate CRC")
        calculate_crc_btn.clicked.connect(self.on_calculate_crc)
        action_layout.addWidget(calculate_crc_btn)
        
        validate_btn = QPushButton("Validate Against DAT")
        validate_btn.clicked.connect(self.on_validate)
        action_layout.addWidget(validate_btn)
        
        organize_btn = QPushButton("Organize to Output Folder")
        organize_btn.clicked.connect(self.on_organize_roms)
        action_layout.addWidget(organize_btn)
        
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def browse_input_directory(self):
        """Browse for input directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Input ROM Folder",
            self.input_directory or os.path.expanduser("~")
        )
        if directory:
            self.input_directory = directory
            self.input_label.setText(directory)
            logger.info(f"Input directory set to: {directory}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Folder for Organized ROMs",
            self.output_directory or os.path.expanduser("~")
        )
        if directory:
            self.output_directory = directory
            self.output_label.setText(directory)
            logger.info(f"Output directory set to: {directory}")
    
    def browse_directory(self):
        """Browse for directory (legacy)."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_label.setText(directory)
            self.scan_directory(directory)
    
    def scan_directory(self, directory: str):
        """Scan directory for ROMs."""
        from src.core.rom_scanner import ROMScanner
        
        scanner = ROMScanner()
        result = scanner.scan_directory(
            directory,
            recursive=self.recursive_check.isChecked()
        )
        
        self.scanned_files = result['roms']
        self.populate_table(result['roms'])
        logger.info(f"Scanned directory: {directory}, found {len(self.scanned_files)} ROMs")
    
    def populate_table(self, files: list):
        """Populate files table."""
        self.files_table.setRowCount(0)
        
        for i, file_info in enumerate(files):
            self.files_table.insertRow(i)
            
            self.files_table.setItem(i, 0, QTableWidgetItem(file_info['filename']))
            self.files_table.setItem(i, 1, QTableWidgetItem(file_info.get('system', 'Unknown')))
            self.files_table.setItem(i, 2, QTableWidgetItem(self._format_size(file_info['size'])))
            self.files_table.setItem(i, 3, QTableWidgetItem("-"))
            self.files_table.setItem(i, 4, QTableWidgetItem("Pending"))
            self.files_table.setItem(i, 5, QTableWidgetItem("-"))
    
    def on_scan_clicked(self):
        """Handle scan button click."""
        if self.input_directory and self.input_directory != "No directory selected":
            self.scan_directory(self.input_directory)
        elif self.dir_label.text() != "No directory selected":
            self.scan_directory(self.dir_label.text())
        else:
            logger.warning("Please select a directory first")
    
    def on_calculate_crc(self):
        """Calculate CRC for selected files."""
        from src.core.crc_calculator import CRCCalculator
        from PyQt6.QtCore import QTimer
        
        if not self.scanned_files:
            logger.warning("No files to process")
            return
        
        # Calculate CRC in background
        calculator = CRCCalculator()
        
        def update_table(file_path, success, crc, completed, total):
            for i, file_info in enumerate(self.scanned_files):
                if file_info['path'] == file_path:
                    self.files_table.setItem(i, 3, QTableWidgetItem(crc or "-"))
                    
                    status = "✓ OK" if success else "✗ Error"
                    status_item = self.files_table.item(i, 4)
                    if status_item:
                        status_item.setText(status)
                        if success:
                            status_item.setBackground(QColor(200, 255, 200))
                        else:
                            status_item.setBackground(QColor(255, 200, 200))
                    break
        
        file_paths = [f['path'] for f in self.scanned_files]
        results = calculator.calculate_batch_crc(file_paths, progress_callback=update_table)
        logger.info(f"Calculated CRC for {len(results)} files")
    
    def on_validate(self):
        """Validate against DAT database."""
        logger.info("Validation feature coming soon")
    
    def on_organize_roms(self):
        """Organize ROMs to output folder with manufacturer/system structure."""
        from src.core.system_map import get_manufacturer
        
        if not self.output_directory:
            logger.warning("Please select an output folder first")
            return
        
        if not self.scanned_files:
            logger.warning("No ROM files to organize")
            return
        
        logger.info(f"Organizing ROMs to: {self.output_directory}")
        
        # Create manufacturer/system subdirectories and copy files
        import shutil
        
        organized_count = 0
        for file_info in self.scanned_files:
            system = file_info.get('system', 'Unknown')
            manufacturer = get_manufacturer(system)
            
            # Create directory structure: Manufacturer/System
            system_dir = os.path.join(self.output_directory, manufacturer, system)
            
            os.makedirs(system_dir, exist_ok=True)
            
            # Copy file to manufacturer/system directory
            try:
                source_path = file_info['path']
                dest_path = os.path.join(system_dir, file_info['filename'])
                
                if not os.path.exists(dest_path):
                    shutil.copy2(source_path, dest_path)
                    organized_count += 1
                    logger.info(f"Organized: {file_info['filename']} -> {manufacturer}/{system}/")
                else:
                    logger.info(f"Skipped (already exists): {file_info['filename']}")
            except Exception as e:
                logger.error(f"Error organizing {file_info['filename']}: {e}")
        
        logger.info(f"Successfully organized {organized_count} ROM files")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


class ArchiveTab(QWidget):
    """Tab for processing ROM archives."""
    
    def __init__(self):
        """Initialize archive tab."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        
        # Folder selection
        folder_group = QGroupBox("Archive Processing Configuration")
        folder_layout = QVBoxLayout()
        
        # Input folder for archives
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Archive Input Folder:"))
        self.input_label = QLineEdit()
        self.input_label.setReadOnly(True)
        self.input_label.setPlaceholderText("No folder selected")
        input_layout.addWidget(self.input_label)
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(input_browse_btn)
        folder_layout.addLayout(input_layout)
        
        # Output folder for extracted ROMs
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder (Extracted ROMs):"))
        self.output_label = QLineEdit()
        self.output_label.setReadOnly(True)
        self.output_label.setPlaceholderText("No folder selected")
        output_layout.addWidget(self.output_label)
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(output_browse_btn)
        folder_layout.addLayout(output_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        layout.addWidget(QLabel("Archive extraction and processing features coming soon"))
        layout.addStretch()
        
        self.setLayout(layout)
    
    def browse_input_directory(self):
        """Browse for input archive directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Archive Input Folder",
            os.path.expanduser("~")
        )
        if directory:
            self.input_label.setText(directory)
            logger.info(f"Archive input directory set to: {directory}")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Folder for Extracted ROMs",
            os.path.expanduser("~")
        )
        if directory:
            self.output_label.setText(directory)
            logger.info(f"Archive output directory set to: {directory}")


class ResultsTab(QWidget):
    """Tab for displaying validation results."""
    
    def __init__(self):
        """Initialize results tab."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Filename", "System", "CRC32", "Match Status",
            "Game", "Expected CRC", "Size", "Notes"
        ])
        
        layout.addWidget(QLabel("Validation Results:"))
        layout.addWidget(self.results_table)
        
        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_btn = QPushButton("Export Results to CSV")
        export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(export_btn)
        
        layout.addLayout(export_layout)
        
        self.setLayout(layout)
    
    def export_results(self):
        """Export results to CSV."""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            logger.info(f"Exporting results to {filename}")
