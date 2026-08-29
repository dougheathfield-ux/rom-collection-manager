import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MultiDiscSorter:
    """Detect and organize multi-disc games."""
    
    # Common multi-disc patterns
    DISC_PATTERNS = [
        r'\(Disc (\d+)\)',  # (Disc 1)
        r'\[Disc (\d+)\]',  # [Disc 1]
        r'Disc(\d+)',        # Disc1
        r'CD(\d+)',          # CD1
        r'Disk(\d+)',        # Disk1
        r'(?:^|\s)(\d+)(?:of|of|\s|\))',  # 1 of 4 or similar
    ]
    
    def __init__(self):
        """Initialize multi-disc sorter."""
        self.disc_groups = {}
    
    def detect_disc_number(self, filename: str) -> Optional[int]:
        """
        Detect disc number from filename.
        
        Args:
            filename: ROM filename
            
        Returns:
            Disc number (1-based) or None
        """
        for pattern in self.DISC_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    disc_num = int(match.group(1))
                    if disc_num > 0:
                        return disc_num
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_base_name(self, filename: str) -> str:
        """
        Extract base game name without disc number.
        
        Args:
            filename: ROM filename
            
        Returns:
            Base game name
        """
        # Remove disc patterns
        base = filename
        for pattern in self.DISC_PATTERNS:
            base = re.sub(pattern, '', base, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation
        base = re.sub(r'\s+', ' ', base).strip()
        base = re.sub(r'[()\[\]]+$', '', base).strip()
        
        return base
    
    def group_multi_disc_files(self, file_list: List[str]) -> Dict[str, Dict]:
        """
        Group files by game and disc number.
        
        Args:
            file_list: List of ROM filenames
            
        Returns:
            Dictionary of game_name -> disc_info
        """
        groups = {}
        
        for filename in file_list:
            disc_num = self.detect_disc_number(filename)
            
            if disc_num is None:
                # Single file game
                base_name = filename
                disc_num = 1
            else:
                base_name = self.extract_base_name(filename)
            
            if base_name not in groups:
                groups[base_name] = {
                    'base_name': base_name,
                    'is_multi_disc': False,
                    'discs': {},
                    'total_discs': 1
                }
            
            groups[base_name]['discs'][disc_num] = filename
        
        # Update multi-disc flag
        for game_info in groups.values():
            if len(game_info['discs']) > 1:
                game_info['is_multi_disc'] = True
                game_info['total_discs'] = max(game_info['discs'].keys())
        
        return groups
    
    def validate_multi_disc_set(self, disc_files: Dict[int, str]) -> Tuple[bool, List[str]]:
        """
        Validate that all discs are present for a multi-disc game.
        
        Args:
            disc_files: Dictionary of disc_number -> filename
            
        Returns:
            Tuple of (is_complete, missing_discs)
        """
        missing = []
        max_disc = max(disc_files.keys()) if disc_files else 0
        
        for disc_num in range(1, max_disc + 1):
            if disc_num not in disc_files:
                missing.append(f"Disc {disc_num}")
        
        is_complete = len(missing) == 0
        return is_complete, missing
    
    def suggest_naming_convention(self, game_name: str, disc_number: int) -> str:
        """
        Suggest standardized filename for a disc.
        
        Args:
            game_name: Base game name
            disc_number: Disc number
            
        Returns:
            Suggested filename
        """
        return f"{game_name} (Disc {disc_number})"
    
    def get_multi_disc_summary(self, groups: Dict[str, Dict]) -> List[Dict]:
        """
        Get summary of multi-disc games.
        
        Args:
            groups: Grouped files from group_multi_disc_files()
            
        Returns:
            List of multi-disc game summaries
        """
        summaries = []
        
        for game_name, info in groups.items():
            if info['is_multi_disc']:
                is_complete, missing = self.validate_multi_disc_set(info['discs'])
                
                summaries.append({
                    'game': game_name,
                    'disc_count': info['total_discs'],
                    'complete': is_complete,
                    'missing': missing,
                    'discs': list(info['discs'].items())
                })
        
        return summaries
