# Development & Contribution Guide

## Setting Up Development Environment

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/dougheathfield-ux/rom-collection-manager.git
cd rom-collection-manager
pip install -r requirements.txt
```

### 2. Install Development Dependencies

```bash
pip install pytest pytest-cov black flake8 mypy
```

## Project Architecture

### Core Layer (`src/core/`)
High-level business logic independent of UI:
- CRC calculation and ROM validation
- Archive handling and extraction
- DAT file parsing and matching
- System dependency management
- Multi-disc game organization
- ROM file scanning and cataloging

### GUI Layer (`src/gui/`)
PyQt6-based user interface:
- Main window with menu bar
- Tabbed interface (Local Files, Archives, Results)
- Dialog windows for specific tasks
- Event handling and user interactions
- Result display and export

## Code Style

The project follows PEP 8 conventions:

```bash
# Format code with black
black src/ main.py

# Check style with flake8
flake8 src/ main.py

# Type checking with mypy
mypy src/ main.py
```

## Testing

### Running Tests

```bash
pytest tests/
```

### Coverage Report

```bash
pytest --cov=src tests/
```

## Adding New Features

### 1. Create Core Module

If adding new functionality, create a module in `src/core/`:

```python
# src/core/my_feature.py
import logging

logger = logging.getLogger(__name__)

class MyFeature:
    """Description of the feature."""
    
    def __init__(self):
        """Initialize."""
        pass
    
    def do_something(self):
        """Do something."""
        logger.info("Doing something")
```

### 2. Integrate with GUI

Add UI components in `src/gui/`:

```python
# src/gui/tabs.py or dialogs.py
from src.core.my_feature import MyFeature

class MyFeatureTab(QWidget):
    def __init__(self):
        super().__init__()
        self.feature = MyFeature()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements."""
        # Create UI
        pass
```

### 3. Add Tests

Create corresponding test file:

```python
# tests/test_my_feature.py
import pytest
from src.core.my_feature import MyFeature

def test_my_feature():
    feature = MyFeature()
    result = feature.do_something()
    assert result is not None
```

## Git Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Add: my feature description"
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/my-feature
   ```

4. Create a Pull Request

## Commit Message Format

Use descriptive commit messages:

- `Add:` - New features
- `Fix:` - Bug fixes
- `Refactor:` - Code restructuring
- `Test:` - Adding or updating tests
- `Docs:` - Documentation updates
- `Chore:` - Maintenance tasks

Example:
```
Add: CRC calculation with header stripping support

- Detect NES/SNES headers automatically
- Strip headers before CRC calculation
- Maintain original file integrity
```

## Debugging

### Enable Debug Logging

Modify logging level in `main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### PyQt Debugging

Set environment variables before running:

```bash
export QT_DEBUG_PLUGINS=1
python main.py
```

## Performance Considerations

1. **Parallel Processing** - Use ThreadPoolExecutor for CPU-bound tasks
2. **File I/O** - Use buffered reading for large files
3. **GUI Responsiveness** - Move long operations to background threads
4. **Memory Usage** - Stream archives instead of loading into memory

## Documentation

All modules should include:
- Module docstring with description
- Class docstrings with purpose
- Method docstrings with args and returns
- Inline comments for complex logic

Example:

```python
def calculate_crc32(self, file_path: str) -> int:
    """
    Calculate CRC32 checksum for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        CRC32 checksum as integer
        
    Raises:
        IOError: If file cannot be read
    """
```

## Release Checklist

- [ ] All tests passing
- [ ] Code formatted with black
- [ ] No flake8 errors
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] README updated if needed
- [ ] CHANGELOG updated
- [ ] Version bumped in `src/__init__.py`
- [ ] Tag created: `git tag v0.x.x`

## Troubleshooting

### Import Errors

```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py
```

### PyQt6 Issues

```bash
# Reinstall PyQt6
pip install --upgrade --force-reinstall PyQt6
```

### Archive Extraction Issues

```bash
# Check for required system tools
which 7z
which unzip
which rar
```

## Questions or Issues?

Please create an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
