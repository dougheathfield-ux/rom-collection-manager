# ROM Collection Manager

A comprehensive GUI application for managing ROM collections with CRC validation, metadata synchronization with Libretro, and archive handling for No-Intro and Redump databases.

## Features

### Core Features

1. **Software Dependency Checker** - Check and install all required dependencies from the GUI
2. **DAT File Downloader** - Download individual DAT files from No-Intro, TOSEC, and Redump directly in the GUI
3. **Automatic Header Stripping** - Automatically detect and strip NES/SNES ROM headers before CRC calculation
4. **Multi-System Support** - Support for all known gaming systems (NES, SNES, Genesis, N64, PlayStation, etc.)
5. **Libretro Integration** - Connect to Libretro's metadata repository for live, dynamic system lists
6. **Parallel CRC Processing** - Calculate CRC32 checksums in parallel using multi-threading for large collections
7. **Archive Support** - Handle .zip, .7z, .rar, .tar, and other archive formats
8. **Multi-Disc Organization** - Detect, group, and organize multi-disc games
9. **Archive Inspection** - Open archives to check CRC of files inside without full extraction
10. **GUI Results Display** - Show input files and matched output files side-by-side with detailed information

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dougheathfield-ux/rom-collection-manager.git
cd rom-collection-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use the built-in dependency checker from the GUI:
- Launch the application and go to Tools → Check Dependencies
- Click "Install Missing" to automatically install missing packages

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. **Check Dependencies** (Tools → Check Dependencies)
   - Verifies all required Python packages and system tools
   - Option to install missing dependencies with one click

2. **Download DAT Files** (Tools → Download DAT Files)
   - Browse available No-Intro, Redump, and TOSEC systems
   - Select systems to download their DAT files
   - Files are cached locally for offline use

3. **Scan ROM Collection** (File → Open Directory or Local Files tab)
   - Browse to your ROM collection directory
   - Scans for all supported ROM files and archives
   - Displays found files with system information

4. **Calculate CRC Checksums**
   - Select ROMs to process
   - Click "Calculate CRC" to compute checksums
   - Automatic header stripping for NES/SNES ROMs
   - Parallel processing for large collections

5. **Validate Against DAT Files**
   - Matches calculated CRCs against loaded DAT databases
   - Shows match status, game info, and warnings
   - Identifies duplicates and unmatched files

6. **Export Results**
   - Export validation results to CSV
   - View comprehensive matching details
   - Organize ROMs based on validation results

## Project Structure

```
rom-collection-manager/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── src/
    ├── __init__.py
    ├── core/                        # Core functionality
    │   ├── __init__.py
    │   ├── crc_calculator.py        # CRC32 calculation with threading
    │   ├── archive_handler.py       # Archive format support
    │   ├── dat_parser.py            # DAT file parsing
    │   ├── libretro_integration.py  # Libretro metadata integration
    │   ├── dependency_checker.py    # Dependency checking & installation
    │   ├── multi_disc_sorter.py     # Multi-disc game organization
    │   └── rom_scanner.py           # ROM file scanning
    └── gui/                         # GUI components
        ├── __init__.py
        ├── main_window.py           # Main application window
        ├── tabs.py                  # UI tabs (Local Files, Archives, Results)
        └── dialogs.py               # Dialog windows
```

## Core Modules

### CRC Calculator (`src/core/crc_calculator.py`)
- Calculate CRC32 checksums for individual files
- Detect NES headers (iNES format)
- Detect SNES headers (multiple formats)
- Automatic header stripping before CRC calculation
- Parallel batch processing with progress callbacks

### Archive Handler (`src/core/archive_handler.py`)
- Support for .zip, .7z, .rar archives
- List archive contents without extraction
- Extract individual files to temporary locations
- Automatic cleanup of temporary files
- Memory-efficient processing

### DAT Parser (`src/core/dat_parser.py`)
- Parse Logiqx format DAT files
- Support for No-Intro, Redump, TOSEC databases
- CRC lookup and validation
- Multiple DAT file handling
- Game and ROM information retrieval

### Libretro Integration (`src/core/libretro_integration.py`)
- Connect to Libretro metadata repository
- Fetch live system lists for No-Intro and Redump
- Local caching with automatic refresh
- Support for multiple DAT collections

### Dependency Checker (`src/core/dependency_checker.py`)
- Check Python package installation status
- Verify system tool availability (7z, unzip, rar, etc.)
- Platform-specific installation support (Linux, macOS, Windows)
- Automatic installation with appropriate package managers

### Multi-Disc Sorter (`src/core/multi_disc_sorter.py`)
- Detect multi-disc game patterns in filenames
- Group disc files together
- Validate disc set completeness
- Suggest standardized naming conventions
- Support for various disc numbering schemes

### ROM Scanner (`src/core/rom_scanner.py`)
- Recursively scan directories for ROM files
- Support for multiple archive formats
- Identify ROM systems from file extensions
- Filter by system or file type

## Configuration

The application automatically creates a cache directory at `~/.rcm_cache` for:
- Libretro system metadata
- Downloaded DAT files
- Temporary archive extractions

## System Requirements

### Supported Operating Systems
- Windows 10 or later
- macOS 10.13 or later
- Linux (Ubuntu, Fedora, Arch, etc.)

### System Dependencies
- **7-Zip** - For .7z archive support
- **unzip** - For .zip archive support (usually pre-installed)
- **rar** - For .rar archive support (optional)

## Dependencies

See `requirements.txt` for full list of Python dependencies:
- PyQt6 - GUI framework
- requests - HTTP requests for Libretro integration
- py7zr - 7-Zip archive support
- rarfile - RAR archive support
- lxml - XML parsing for DAT files
- Pillow - Image processing

## Known Limitations

- RAR archive support requires WinRAR or compatible libraries
- Some archive formats may require external tools to be installed
- Very large ROM collections (10,000+) may take time for initial scanning

## Future Enhancements

- SHA1 and MD5 checksum support
- Automatic ROM renaming and organization
- BIOS file management
- Game metadata display (cover art, descriptions, ratings)
- Multi-threading improvements for archive processing
- Database export for emulator frontends (Attract-Mode, RetroFE, etc.)
- Duplicate detection and removal
- Regional variant detection

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the project.

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or suggestions, please create an issue on the GitHub repository.

## Acknowledgments

- [No-Intro](https://www.no-intro.org/) - ROM database maintainers
- [Redump](http://redump.org/) - Preservation project
- [Libretro](https://www.libretro.com/) - Emulation ecosystem
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
