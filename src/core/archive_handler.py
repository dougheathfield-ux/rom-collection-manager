import os
import tempfile
import zipfile
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import py7zr

logger = logging.getLogger(__name__)

try:
    import rarfile
    HAS_RARFILE = True
except ImportError:
    HAS_RARFILE = False


class ArchiveHandler:
    """Handle various archive formats (.zip, .7z, .rar, etc.)."""
    
    SUPPORTED_FORMATS = {
        '.zip': 'ZIP',
        '.7z': '7-Zip',
        '.rar': 'RAR',
        '.tar': 'TAR',
        '.gz': 'GZIP',
        '.bz2': 'BZIP2',
    }
    
    def __init__(self):
        """Initialize archive handler."""
        self.temp_dir = None
    
    def get_supported_formats(self) -> Dict[str, str]:
        """Get dictionary of supported archive formats."""
        formats = self.SUPPORTED_FORMATS.copy()
        if not HAS_RARFILE:
            formats.pop('.rar', None)
        return formats
    
    def is_archive(self, file_path: str) -> bool:
        """
        Check if file is a supported archive format.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is a supported archive
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def get_archive_type(self, file_path: str) -> Optional[str]:
        """
        Determine archive type.
        
        Args:
            file_path: Path to archive file
            
        Returns:
            Archive type string or None
        """
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_FORMATS.get(ext)
    
    def list_archive_contents(self, archive_path: str) -> List[Dict]:
        """
        List contents of archive without extracting.
        
        Args:
            archive_path: Path to archive file
            
        Returns:
            List of file info dictionaries
        """
        contents = []
        
        try:
            archive_type = self.get_archive_type(archive_path)
            
            if archive_type == 'ZIP':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    for info in zf.infolist():
                        if not info.is_dir():
                            contents.append({
                                'filename': info.filename,
                                'size': info.file_size,
                                'compressed_size': info.compress_size,
                                'is_dir': False
                            })
            
            elif archive_type == '7-Zip':
                with py7zr.SevenZipFile(archive_path, 'r') as szf:
                    for name, info in szf.list():
                        if not info.is_directory:
                            contents.append({
                                'filename': name,
                                'size': info.uncompressed,
                                'compressed_size': info.compressed,
                                'is_dir': False
                            })
            
            elif archive_type == 'RAR' and HAS_RARFILE:
                with rarfile.RarFile(archive_path, 'r') as rf:
                    for info in rf.infolist():
                        if not info.is_dir():
                            contents.append({
                                'filename': info.filename,
                                'size': info.file_size,
                                'compressed_size': info.compress_size,
                                'is_dir': False
                            })
            
            return contents
        
        except Exception as e:
            logger.error(f"Error listing archive contents for {archive_path}: {e}")
            return []
    
    def extract_file_from_archive(self, archive_path: str, 
                                 file_name: str, 
                                 output_dir: Optional[str] = None) -> Optional[str]:
        """
        Extract a single file from archive to temporary location.
        
        Args:
            archive_path: Path to archive file
            file_name: Name of file to extract
            output_dir: Optional output directory (uses temp if None)
            
        Returns:
            Path to extracted file or None on error
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
                self.temp_dir = output_dir
            
            archive_type = self.get_archive_type(archive_path)
            
            if archive_type == 'ZIP':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extract(file_name, output_dir)
            
            elif archive_type == '7-Zip':
                with py7zr.SevenZipFile(archive_path, 'r') as szf:
                    szf.extract(targets=[file_name], path=output_dir)
            
            elif archive_type == 'RAR' and HAS_RARFILE:
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extract(file_name, output_dir)
            
            extracted_path = os.path.join(output_dir, file_name)
            if os.path.exists(extracted_path):
                return extracted_path
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting {file_name} from {archive_path}: {e}")
            return None
    
    def extract_all(self, archive_path: str, 
                   output_dir: Optional[str] = None) -> Optional[str]:
        """
        Extract all files from archive.
        
        Args:
            archive_path: Path to archive file
            output_dir: Optional output directory (uses temp if None)
            
        Returns:
            Path to extraction directory or None on error
        """
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
                self.temp_dir = output_dir
            
            archive_type = self.get_archive_type(archive_path)
            
            if archive_type == 'ZIP':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(output_dir)
            
            elif archive_type == '7-Zip':
                with py7zr.SevenZipFile(archive_path, 'r') as szf:
                    szf.extractall(path=output_dir)
            
            elif archive_type == 'RAR' and HAS_RARFILE:
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extractall(output_dir)
            
            return output_dir
        
        except Exception as e:
            logger.error(f"Error extracting archive {archive_path}: {e}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary extraction directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                logger.info("Cleaned up temporary files")
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {e}")
    
    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup_temp_files()
