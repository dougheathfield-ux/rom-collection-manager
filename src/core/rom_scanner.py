import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ROMScanner:
    """Scan directories for ROM files and archives."""
    
    # Common ROM file extensions by system
    ROM_EXTENSIONS = {
        # Nintendo
        '.nes': 'NES',
        '.snes': 'SNES',
        '.n64': 'N64',
        '.gb': 'Game Boy',
        '.gbc': 'Game Boy Color',
        '.gba': 'Game Boy Advance',
        '.nds': 'Nintendo DS',
        '.3ds': 'Nintendo 3DS',
        '.gcn': 'GameCube',
        '.iso': 'GameCube/Wii/PS1/PS2/Wii U',
        '.wii': 'Wii',
        '.wud': 'Wii U',
        '.nsp': 'Switch',
        '.xci': 'Switch',
        
        # Sega
        '.gen': 'Genesis',
        '.md': 'Genesis',
        '.gg': 'Game Gear',
        '.sms': 'Master System',
        '.32x': '32X',
        '.sat': 'Saturn',
        '.bin': 'Saturn/Dreamcast',
        '.cue': 'Saturn/Dreamcast',
        '.gdi': 'Dreamcast',
        
        # Sony
        '.cso': 'PSP/PS Vita',
        '.vpk': 'PS Vita',
        '.psv': 'PS Vita',
        '.pbp': 'PSP',
        
        # Atari
        '.a26': 'Atari 2600',
        '.a78': 'Atari 7800',
        '.lnx': 'Atari Lynx',
        
        # Other
        '.zip': 'Archive',
        '.7z': 'Archive',
        '.rar': 'Archive',
        '.tar': 'Archive',
    }
    
    ARCHIVE_EXTENSIONS = {'.zip', '.7z', '.rar', '.tar', '.gz', '.bz2'}
    
    def __init__(self):
        """Initialize ROM scanner."""
        self.found_roms = []
        self.found_archives = []
    
    def scan_directory(self, directory: str, recursive: bool = True) -> Dict:
        """
        Scan directory for ROM files and archives.
        
        Args:
            directory: Path to directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            Dictionary with 'roms' and 'archives' lists
        """
        self.found_roms = []
        self.found_archives = []
        
        if not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            return {'roms': [], 'archives': []}
        
        try:
            if recursive:
                self._scan_recursive(directory)
            else:
                self._scan_directory_flat(directory)
            
            logger.info(f"Found {len(self.found_roms)} ROMs and {len(self.found_archives)} archives")
            
            return {
                'roms': self.found_roms,
                'archives': self.found_archives,
                'total': len(self.found_roms) + len(self.found_archives)
            }
        
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            return {'roms': [], 'archives': []}
    
    def _scan_directory_flat(self, directory: str):
        """Scan single directory (non-recursive)."""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path):
                    self._check_file(item_path)
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
    
    def _scan_recursive(self, directory: str):
        """Scan directory recursively."""
        try:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    self._check_file(file_path)
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
    
    def _check_file(self, file_path: str):
        """Check if file is a ROM or archive."""
        try:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            file_size = os.path.getsize(file_path)
            
            if ext in self.ARCHIVE_EXTENSIONS:
                self.found_archives.append({
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': file_size,
                    'extension': ext,
                    'type': 'Archive'
                })
            
            elif ext in self.ROM_EXTENSIONS:
                system = self.ROM_EXTENSIONS.get(ext, 'Unknown')
                self.found_roms.append({
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': file_size,
                    'extension': ext,
                    'system': system,
                    'type': 'ROM'
                })
        
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
    
    def filter_by_extension(self, files: List[Dict], extension: str) -> List[Dict]:
        """Filter files by extension."""
        ext = extension.lower() if extension.startswith('.') else f'.{extension.lower()}'
        return [f for f in files if f['extension'] == ext]
    
    def filter_by_system(self, roms: List[Dict], system: str) -> List[Dict]:
        """Filter ROMs by system."""
        return [r for r in roms if r.get('system') == system]
    
    def get_systems_found(self, roms: List[Dict]) -> List[str]:
        """Get list of unique systems found."""
        systems = set()
        for rom in roms:
            if 'system' in rom:
                systems.add(rom['system'])
        return sorted(list(systems))
