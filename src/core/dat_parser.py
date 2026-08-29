import logging
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


class DATParser:
    """Parse DAT files (No-Intro, Redump, TOSEC formats)."""
    
    def __init__(self):
        """Initialize DAT parser."""
        self.games = []
        self.roms = {}
    
    def parse_dat_file(self, file_path: str) -> bool:
        """
        Parse DAT file in Logiqx format.
        
        Args:
            file_path: Path to DAT file
            
        Returns:
            True if parsing successful
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            if root.tag != 'datafile':
                logger.warning(f"Unexpected root tag: {root.tag}")
                return False
            
            self.games = []
            self.roms = {}
            
            for game in root.findall('game'):
                game_name = game.get('name')
                if game_name:
                    self.games.append(game_name)
                    
                    for rom in game.findall('rom'):
                        rom_name = rom.get('name')
                        rom_crc = rom.get('crc')
                        rom_md5 = rom.get('md5')
                        rom_sha1 = rom.get('sha1')
                        rom_size = rom.get('size')
                        
                        if rom_crc:
                            self.roms[rom_crc.upper()] = {
                                'name': rom_name,
                                'game': game_name,
                                'crc': rom_crc.upper(),
                                'md5': rom_md5,
                                'sha1': rom_sha1,
                                'size': int(rom_size) if rom_size else None
                            }
            
            logger.info(f"Parsed DAT file: {len(self.games)} games, {len(self.roms)} ROMs")
            return True
        
        except Exception as e:
            logger.error(f"Error parsing DAT file {file_path}: {e}")
            return False
    
    def lookup_by_crc(self, crc_value: str) -> Optional[Dict]:
        """
        Look up ROM by CRC value.
        
        Args:
            crc_value: CRC32 value as string (uppercase hex)
            
        Returns:
            ROM info dictionary or None
        """
        return self.roms.get(crc_value.upper())
    
    def lookup_by_size_and_crc(self, size: int, crc_value: str) -> Optional[Dict]:
        """
        Look up ROM by size and CRC (more accurate matching).
        
        Args:
            size: File size in bytes
            crc_value: CRC32 value as string
            
        Returns:
            ROM info dictionary or None
        """
        rom_info = self.roms.get(crc_value.upper())
        if rom_info and rom_info['size'] == size:
            return rom_info
        return None
    
    def get_game_list(self) -> List[str]:
        """Get list of all games in DAT file."""
        return self.games
    
    def get_roms_for_game(self, game_name: str) -> List[Dict]:
        """Get all ROMs for a specific game."""
        return [rom for rom in self.roms.values() if rom['game'] == game_name]
    
    def clear(self):
        """Clear all loaded data."""
        self.games = []
        self.roms = {}


class MultiDATPatcher:
    """Handle matching across multiple DAT files."""
    
    def __init__(self):
        """Initialize multi-DAT patcher."""
        self.dat_files = {}
        self.all_roms = {}
    
    def load_dat(self, system_name: str, file_path: str) -> bool:
        """
        Load a DAT file for a system.
        
        Args:
            system_name: Name of gaming system
            file_path: Path to DAT file
            
        Returns:
            True if loaded successfully
        """
        parser = DATParser()
        if parser.parse_dat_file(file_path):
            self.dat_files[system_name] = parser
            
            # Merge into all_roms with system prefix
            for crc, rom_info in parser.roms.items():
                key = f"{system_name}:{crc}"
                self.all_roms[key] = {**rom_info, 'system': system_name}
            
            return True
        return False
    
    def lookup_by_crc(self, crc_value: str) -> List[Dict]:
        """
        Look up ROM by CRC across all loaded DAT files.
        
        Args:
            crc_value: CRC32 value as string
            
        Returns:
            List of matching ROM info dictionaries
        """
        matches = []
        crc_upper = crc_value.upper()
        
        for system, parser in self.dat_files.items():
            rom_info = parser.lookup_by_crc(crc_upper)
            if rom_info:
                matches.append({**rom_info, 'system': system})
        
        return matches
    
    def get_loaded_systems(self) -> List[str]:
        """Get list of loaded DAT systems."""
        return list(self.dat_files.keys())
    
    def clear(self):
        """Clear all loaded DATs."""
        self.dat_files.clear()
        self.all_roms.clear()
