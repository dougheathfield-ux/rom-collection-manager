import requests
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class LibretroMetadataManager:
    """
    Integrate with Libretro's metadata repository for live system lists.
    
    Connects to Libretro's GitHub repository to dynamically fetch supported
    systems for No-Intro and Redump databases.
    """
    
    # Libretro metadata repository
    LIBRETRO_REPO_URL = "https://raw.githubusercontent.com/libretro/libretro-database/master"
    LIBRETRO_METADATA_LISTS = f"{LIBRETRO_REPO_URL}/metadat"
    
    # Metadata file locations
    NOINTRO_DAT_LIST = f"{LIBRETRO_METADATA_LISTS}/No-Intro.txt"
    REDUMP_DAT_LIST = f"{LIBRETRO_METADATA_LISTS}/Redump.txt"
    TOSEC_DAT_LIST = f"{LIBRETRO_METADATA_LISTS}/TOSEC.txt"
    
    # Fallback systems if network fetch fails
    FALLBACK_SYSTEMS = {
        'No-Intro': {
            'NES': {'name': 'NES', 'dat_collection': 'No-Intro'},
            'SNES': {'name': 'SNES', 'dat_collection': 'No-Intro'},
            'Genesis': {'name': 'Genesis', 'dat_collection': 'No-Intro'},
            'Game Boy': {'name': 'Game Boy', 'dat_collection': 'No-Intro'},
            'Game Boy Color': {'name': 'Game Boy Color', 'dat_collection': 'No-Intro'},
            'Game Boy Advance': {'name': 'Game Boy Advance', 'dat_collection': 'No-Intro'},
            'N64': {'name': 'N64', 'dat_collection': 'No-Intro'},
            'Nintendo DS': {'name': 'Nintendo DS', 'dat_collection': 'No-Intro'},
        },
        'Redump': {
            'PlayStation': {'name': 'PlayStation', 'dat_collection': 'Redump'},
            'PlayStation 2': {'name': 'PlayStation 2', 'dat_collection': 'Redump'},
            'Dreamcast': {'name': 'Dreamcast', 'dat_collection': 'Redump'},
            'Saturn': {'name': 'Saturn', 'dat_collection': 'Redump'},
        },
        'TOSEC': {
            'Atari 2600': {'name': 'Atari 2600', 'dat_collection': 'TOSEC'},
            'Atari 7800': {'name': 'Atari 7800', 'dat_collection': 'TOSEC'},
            'Arcade': {'name': 'Arcade', 'dat_collection': 'TOSEC'},
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Libretro metadata manager.
        
        Args:
            cache_dir: Directory for caching metadata (default: ~/.rcm_cache)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.rcm_cache")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.systems = {}
        self.last_update = None
        self.cache_file = os.path.join(cache_dir, "systems_cache.json")
        
        # Load cache first, then initialize with fallback if empty
        self._load_cache()
        
        # If no cache, use fallback systems
        if not self.systems:
            self.systems = self.FALLBACK_SYSTEMS.copy()
            logger.info("Using fallback system lists")
    
    def fetch_nointro_systems(self) -> Dict[str, Dict]:
        """
        Fetch list of No-Intro supported systems from Libretro.
        
        Returns:
            Dictionary of system info keyed by system name
        """
        return self._fetch_dat_systems("No-Intro", self.NOINTRO_DAT_LIST)
    
    def fetch_redump_systems(self) -> Dict[str, Dict]:
        """
        Fetch list of Redump supported systems from Libretro.
        
        Returns:
            Dictionary of system info keyed by system name
        """
        return self._fetch_dat_systems("Redump", self.REDUMP_DAT_LIST)
    
    def fetch_tosec_systems(self) -> Dict[str, Dict]:
        """
        Fetch list of TOSEC supported systems from Libretro.
        
        Returns:
            Dictionary of system info keyed by system name
        """
        return self._fetch_dat_systems("TOSEC", self.TOSEC_DAT_LIST)
    
    def _fetch_dat_systems(self, dat_name: str, url: str) -> Dict[str, Dict]:
        """
        Fetch DAT system list from URL.
        
        Args:
            dat_name: Name of DAT collection (No-Intro, Redump, TOSEC)
            url: URL to fetch from
            
        Returns:
            Dictionary of system information
        """
        systems = {}
        
        try:
            logger.info(f"Fetching {dat_name} systems from Libretro...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Format is typically: system_name|dat_filename or similar
                    parts = line.split('|')
                    if len(parts) >= 1:
                        system_name = parts[0].strip()
                        if system_name:  # Only add non-empty names
                            systems[system_name] = {
                                'name': system_name,
                                'dat_collection': dat_name,
                                'dat_filename': parts[1].strip() if len(parts) > 1 else None,
                                'fetched_at': datetime.now().isoformat()
                            }
            
            if systems:
                logger.info(f"Successfully fetched {len(systems)} {dat_name} systems")
            else:
                logger.warning(f"No systems found for {dat_name}, using fallback")
                systems = self.FALLBACK_SYSTEMS.get(dat_name, {})
            
            return systems
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {dat_name} systems: {e}")
            logger.info(f"Using fallback systems for {dat_name}")
            return self.FALLBACK_SYSTEMS.get(dat_name, {})
        except Exception as e:
            logger.error(f"Error parsing {dat_name} systems: {e}")
            return self.FALLBACK_SYSTEMS.get(dat_name, {})
    
    def refresh_all_systems(self) -> bool:
        """
        Refresh all system lists from Libretro repository.
        
        Returns:
            True if refresh successful
        """
        try:
            nointro = self.fetch_nointro_systems()
            redump = self.fetch_redump_systems()
            tosec = self.fetch_tosec_systems()
            
            self.systems = {
                'No-Intro': nointro,
                'Redump': redump,
                'TOSEC': tosec,
            }
            
            self.last_update = datetime.now()
            self._save_cache()
            
            logger.info("Successfully refreshed all system lists")
            return True
        
        except Exception as e:
            logger.error(f"Error refreshing systems: {e}")
            return False
    
    def get_systems_by_collection(self, collection: str) -> Dict[str, Dict]:
        """
        Get systems for a specific DAT collection.
        
        Args:
            collection: Collection name (No-Intro, Redump, or TOSEC)
            
        Returns:
            Dictionary of systems
        """
        return self.systems.get(collection, {})
    
    def get_all_systems(self) -> Dict:
        """Get all cached systems organized by collection."""
        return self.systems
    
    def is_cache_valid(self, max_age_hours: int = 24) -> bool:
        """
        Check if cache is still valid.
        
        Args:
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            True if cache is valid
        """
        if not self.last_update:
            return False
        
        age_hours = (datetime.now() - self.last_update).total_seconds() / 3600
        return age_hours < max_age_hours
    
    def _save_cache(self):
        """Save systems to local cache."""
        try:
            cache_data = {
                'systems': self.systems,
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Saved systems cache to {self.cache_file}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _load_cache(self):
        """Load systems from local cache."""
        if not os.path.exists(self.cache_file):
            return
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            self.systems = cache_data.get('systems', {})
            
            if cache_data.get('last_update'):
                self.last_update = datetime.fromisoformat(cache_data['last_update'])
            
            logger.info(f"Loaded systems cache from {self.cache_file}")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
