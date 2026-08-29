import os
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CRCCalculator:
    """Calculate CRC32 checksums for ROM files with parallel processing."""
    
    # NES header signatures
    NES_HEADER = b'NES\x1a'
    
    # SNES header detection patterns
    SNES_HEADER_PATTERNS = [
        (0x7FB0, b'\x00'),  # Standard SNES header location
        (0xFFB0, b'\x00'),  # HiROM variant
    ]
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize CRC calculator with thread pool.
        
        Args:
            max_workers: Number of threads for parallel processing
        """
        self.max_workers = max_workers
        self.buffer_size = 65536  # 64KB buffer for reading files
        
    def calculate_crc32(self, file_path: str) -> int:
        """
        Calculate CRC32 checksum for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            CRC32 checksum as integer
        """
        crc = 0
        try:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(self.buffer_size)
                    if not data:
                        break
                    crc = zlib.crc32(data, crc)
            return crc & 0xffffffff
        except Exception as e:
            logger.error(f"Error calculating CRC for {file_path}: {e}")
            raise
    
    def detect_nes_header(self, file_path: str) -> bool:
        """
        Detect NES ROM header (iNES format).
        
        Args:
            file_path: Path to ROM file
            
        Returns:
            True if NES header detected
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == self.NES_HEADER
        except Exception as e:
            logger.error(f"Error detecting NES header in {file_path}: {e}")
            return False
    
    def detect_snes_header(self, file_path: str) -> Tuple[bool, Optional[int]]:
        """
        Detect SNES ROM header.
        
        Args:
            file_path: Path to ROM file
            
        Returns:
            Tuple of (header_detected, header_size)
        """
        try:
            with open(file_path, 'rb') as f:
                file_size = os.path.getsize(file_path)
                
                # Check for 512-byte header (common SNES header size)
                if file_size % 32768 != 0 and (file_size - 512) % 32768 == 0:
                    return True, 512
                
                # Check header patterns
                for offset, pattern in self.SNES_HEADER_PATTERNS:
                    if file_size > offset:
                        f.seek(offset)
                        data = f.read(len(pattern))
                        if data == pattern:
                            return True, offset
            
            return False, None
        except Exception as e:
            logger.error(f"Error detecting SNES header in {file_path}: {e}")
            return False, None
    
    def strip_nes_header(self, file_path: str, output_path: str) -> bool:
        """
        Strip NES header from ROM file.
        
        Args:
            file_path: Input ROM file path
            output_path: Output file path without header
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'rb') as f_in:
                f_in.seek(16)  # Skip 16-byte iNES header
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"Stripped NES header from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error stripping NES header from {file_path}: {e}")
            return False
    
    def strip_snes_header(self, file_path: str, output_path: str, header_size: int) -> bool:
        """
        Strip SNES header from ROM file.
        
        Args:
            file_path: Input ROM file path
            output_path: Output file path without header
            header_size: Size of header to strip
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'rb') as f_in:
                f_in.seek(header_size)
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"Stripped {header_size}-byte header from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error stripping SNES header from {file_path}: {e}")
            return False
    
    def calculate_crc_with_header_strip(self, file_path: str) -> Tuple[int, bool, str]:
        """
        Calculate CRC with automatic header stripping for NES/SNES.
        
        Args:
            file_path: Path to ROM file
            
        Returns:
            Tuple of (crc32_value, header_was_stripped, header_type)
        """
        import tempfile
        
        header_stripped = False
        header_type = "none"
        
        try:
            # Check for NES header
            if self.detect_nes_header(file_path):
                header_type = "NES"
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                
                if self.strip_nes_header(file_path, tmp_path):
                    crc = self.calculate_crc32(tmp_path)
                    os.unlink(tmp_path)
                    return crc, True, header_type
            
            # Check for SNES header
            snes_detected, header_size = self.detect_snes_header(file_path)
            if snes_detected and header_size:
                header_type = "SNES"
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                
                if self.strip_snes_header(file_path, tmp_path, header_size):
                    crc = self.calculate_crc32(tmp_path)
                    os.unlink(tmp_path)
                    return crc, True, header_type
            
            # No header detected, calculate normal CRC
            crc = self.calculate_crc32(file_path)
            return crc, False, header_type
            
        except Exception as e:
            logger.error(f"Error in calculate_crc_with_header_strip for {file_path}: {e}")
            raise
    
    def calculate_batch_crc(self, file_paths: list, 
                           progress_callback=None) -> Dict[str, Dict]:
        """
        Calculate CRC for multiple files in parallel.
        
        Args:
            file_paths: List of file paths to process
            progress_callback: Optional callback for progress updates (file_path, success, crc)
            
        Returns:
            Dictionary with file paths as keys and CRC info as values
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.calculate_crc_with_header_strip, path): path
                for path in file_paths
            }
            
            completed = 0
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    crc, header_stripped, header_type = future.result()
                    results[file_path] = {
                        'crc32': f'{crc:08X}',
                        'crc32_int': crc,
                        'header_stripped': header_stripped,
                        'header_type': header_type,
                        'success': True,
                        'error': None
                    }
                except Exception as e:
                    results[file_path] = {
                        'crc32': None,
                        'crc32_int': None,
                        'header_stripped': False,
                        'header_type': 'none',
                        'success': False,
                        'error': str(e)
                    }
                
                completed += 1
                if progress_callback:
                    progress_callback(file_path, results[file_path]['success'], 
                                     results[file_path]['crc32'], completed, len(file_paths))
        
        return results
