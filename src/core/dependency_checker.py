import logging
import os
import platform
import subprocess
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class DependencyChecker:
    """Check and install project dependencies."""
    
    # Required Python packages
    PYTHON_PACKAGES = {
        'PyQt6': 'PyQt6==6.6.1',
        'requests': 'requests==2.31.0',
        'py7zr': 'py7zr==0.20.8',
        'rarfile': 'rarfile==4.1',
        'lxml': 'lxml==4.9.3',
        'Pillow': 'Pillow==10.0.1',
    }
    
    # System dependencies by OS
    SYSTEM_DEPENDENCIES = {
        'Linux': {
            '7z': 'p7zip-full',
            'unzip': 'unzip',
            'rar': 'rar',  # Optional, not in standard repos
        },
        'Darwin': {  # macOS
            '7z': 'p7zip',
            'unzip': 'unzip',  # Usually pre-installed
        },
        'Windows': {
            '7z': '7-Zip',
            'unzip': 'Built-in',
        }
    }
    
    def __init__(self):
        """Initialize dependency checker."""
        self.os_type = platform.system()
        self.missing_python_packages = []
        self.missing_system_deps = []
    
    def check_python_packages(self) -> Dict[str, bool]:
        """
        Check if required Python packages are installed.
        
        Returns:
            Dictionary of package name -> installed status
        """
        status = {}
        self.missing_python_packages = []
        
        for package_name in self.PYTHON_PACKAGES.keys():
            try:
                __import__(package_name.lower() if package_name != 'PyQt6' else 'PyQt6')
                status[package_name] = True
            except ImportError:
                status[package_name] = False
                self.missing_python_packages.append(package_name)
        
        return status
    
    def check_system_dependencies(self) -> Dict[str, bool]:
        """
        Check if required system utilities are available.
        
        Returns:
            Dictionary of tool name -> installed status
        """
        status = {}
        self.missing_system_deps = []
        
        deps = self.SYSTEM_DEPENDENCIES.get(self.os_type, {})
        
        for tool_name, package_name in deps.items():
            if tool_name == 'unzip' and self.os_type == 'Darwin':
                # unzip is built-in on macOS
                status[tool_name] = True
                continue
            
            if self._is_tool_available(tool_name):
                status[tool_name] = True
            else:
                status[tool_name] = False
                self.missing_system_deps.append((tool_name, package_name))
        
        return status
    
    def check_all(self) -> Tuple[Dict, Dict, bool]:
        """
        Check all dependencies.
        
        Returns:
            Tuple of (python_status, system_status, all_good)
        """
        python_status = self.check_python_packages()
        system_status = self.check_system_dependencies()
        
        all_good = all(python_status.values()) and all(system_status.values())
        
        return python_status, system_status, all_good
    
    def install_python_packages(self) -> bool:
        """
        Install missing Python packages using pip.
        
        Returns:
            True if installation successful
        """
        if not self.missing_python_packages:
            return True
        
        try:
            packages_to_install = [
                self.PYTHON_PACKAGES[pkg] for pkg in self.missing_python_packages
            ]
            
            logger.info(f"Installing Python packages: {packages_to_install}")
            
            subprocess.check_call([
                'pip', 'install', '--upgrade',
                *packages_to_install
            ])
            
            logger.info("Successfully installed Python packages")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing Python packages: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing packages: {e}")
            return False
    
    def install_system_dependencies(self) -> bool:
        """
        Install missing system dependencies.
        
        Note: This requires appropriate permissions and varies by OS.
        
        Returns:
            True if installation successful or not needed
        """
        if not self.missing_system_deps:
            return True
        
        if self.os_type == 'Linux':
            return self._install_linux_deps()
        elif self.os_type == 'Darwin':
            return self._install_macos_deps()
        elif self.os_type == 'Windows':
            return self._install_windows_deps()
        
        logger.warning(f"Unknown OS type: {self.os_type}")
        return False
    
    def _install_linux_deps(self) -> bool:
        """Install dependencies on Linux."""
        try:
            # Detect package manager
            if self._is_tool_available('apt'):
                return self._install_with_apt()
            elif self._is_tool_available('yum'):
                return self._install_with_yum()
            elif self._is_tool_available('pacman'):
                return self._install_with_pacman()
            else:
                logger.warning("No supported package manager found")
                return False
        except Exception as e:
            logger.error(f"Error installing Linux dependencies: {e}")
            return False
    
    def _install_with_apt(self) -> bool:
        """Install using apt (Debian/Ubuntu)."""
        try:
            packages = [pkg for _, pkg in self.missing_system_deps]
            logger.info(f"Installing with apt: {packages}")
            subprocess.check_call(['sudo', 'apt', 'install', '-y', *packages])
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing with apt: {e}")
            return False
    
    def _install_with_yum(self) -> bool:
        """Install using yum (RedHat/CentOS)."""
        try:
            packages = [pkg for _, pkg in self.missing_system_deps]
            logger.info(f"Installing with yum: {packages}")
            subprocess.check_call(['sudo', 'yum', 'install', '-y', *packages])
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing with yum: {e}")
            return False
    
    def _install_with_pacman(self) -> bool:
        """Install using pacman (Arch)."""
        try:
            packages = [pkg for _, pkg in self.missing_system_deps]
            logger.info(f"Installing with pacman: {packages}")
            subprocess.check_call(['sudo', 'pacman', '-S', *packages])
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing with pacman: {e}")
            return False
    
    def _install_macos_deps(self) -> bool:
        """Install dependencies on macOS using Homebrew."""
        try:
            if not self._is_tool_available('brew'):
                logger.error("Homebrew not found. Please install from https://brew.sh")
                return False
            
            packages = [pkg for _, pkg in self.missing_system_deps if pkg != 'unzip']
            if packages:
                logger.info(f"Installing with brew: {packages}")
                subprocess.check_call(['brew', 'install', *packages])
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing macOS dependencies: {e}")
            return False
    
    def _install_windows_deps(self) -> bool:
        """Install dependencies on Windows."""
        logger.info("Windows detected. Please manually install:")
        for tool, package in self.missing_system_deps:
            if tool != 'unzip':
                logger.info(f"  - {package} (https://www.7-zip.org/)")
        return False
    
    @staticmethod
    def _is_tool_available(tool_name: str) -> bool:
        """Check if a command-line tool is available."""
        try:
            subprocess.run(
                ['which', tool_name] if platform.system() != 'Windows' else ['where', tool_name],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_status_summary(self) -> str:
        """Get a human-readable summary of dependency status."""
        python_status, system_status, all_good = self.check_all()
        
        summary = "\n=== Dependency Status ===\n"
        summary += "\nPython Packages:\n"
        for pkg, status in python_status.items():
            summary += f"  {pkg}: {'✓' if status else '✗'}\n"
        
        summary += "\nSystem Dependencies:\n"
        for tool, status in system_status.items():
            summary += f"  {tool}: {'✓' if status else '✗'}\n"
        
        summary += f"\nAll dependencies met: {'Yes' if all_good else 'No'}\n"
        
        return summary
