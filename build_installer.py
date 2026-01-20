#!/usr/bin/env python3
"""
Build script for creating School System Management installer.

This script handles:
1. PyInstaller compilation with error checking
2. Inno Setup installer creation
3. Comprehensive error handling and logging
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_installer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InstallerBuilder:
    """Handles building the installer with comprehensive error handling."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.installer_output = self.project_root / "installer_output"

    def run_command(self, cmd, description, cwd=None, shell=False):
        """Run a command with error handling."""
        logger.info(f"Running: {description}")
        logger.debug(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                shell=shell,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✓ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ {description} failed")
            logger.error(f"Error code: {e.returncode}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error in {description}: {e}")
            return False

    def check_requirements(self):
        """Check if all required tools and dependencies are available."""
        logger.info("Checking build requirements...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 7):
            logger.error(f"Python {python_version.major}.{python_version.minor} is not supported. Need Python 3.7+")
            return False
        logger.info(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")

        # Check if PyInstaller is installed
        try:
            import PyInstaller
            logger.info(f"✓ PyInstaller {PyInstaller.__version__} is available")
        except ImportError:
            logger.error("PyInstaller is not installed. Run: pip install pyinstaller")
            return False

        # Check if Inno Setup is available (on Windows)
        if sys.platform == "win32":
            # Check common Inno Setup installation paths
            inno_paths = [
                r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                r"C:\Program Files\Inno Setup 6\ISCC.exe",
                r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
                r"C:\Program Files\Inno Setup 5\ISCC.exe"
            ]

            self.inno_compiler = None
            for path in inno_paths:
                if os.path.exists(path):
                    self.inno_compiler = path
                    break

            if self.inno_compiler:
                logger.info(f"✓ Inno Setup found at: {self.inno_compiler}")
            else:
                logger.warning("Inno Setup not found. Install from: https://jrsoftware.org/isinfo.php")
                logger.warning("You can still build the executable, but not the installer")
        else:
            logger.info("Non-Windows platform detected - skipping Inno Setup check")

        # Check if required packages are installed
        required_packages = [
            'PyQt6', 'pandas', 'openpyxl', 'fpdf', 'qrcode', 'Pillow'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package} is available")
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.error("Run: pip install -r requirements.txt")
            return False

        return True

    def clean_build_directories(self):
        """Clean previous build artifacts."""
        logger.info("Cleaning build directories...")

        dirs_to_clean = [self.dist_dir, self.build_dir, self.installer_output]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    logger.info(f"✓ Cleaned {dir_path}")
                except Exception as e:
                    logger.warning(f"Could not clean {dir_path}: {e}")

    def validate_spec_file(self):
        """Validate that the PyInstaller spec file exists and is valid."""
        spec_file = self.project_root / "school_system.spec"
        if not spec_file.exists():
            logger.error(f"Spec file not found: {spec_file}")
            return False

        logger.info(f"✓ Spec file found: {spec_file}")
        return True

    def validate_inno_script(self):
        """Validate that the Inno Setup script exists."""
        inno_script = self.project_root / "installer.iss"
        if not inno_script.exists():
            logger.error(f"Inno Setup script not found: {inno_script}")
            return False

        logger.info(f"✓ Inno Setup script found: {inno_script}")
        return True

    def create_version_file(self):
        """Create version information file."""
        version_info = {
            "version": "1.0.0",
            "build_date": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }

        version_file = self.project_root / "version.json"
        try:
            with open(version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
            logger.info(f"✓ Created version file: {version_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create version file: {e}")
            return False

    def build_executable(self):
        """Build the executable using PyInstaller."""
        logger.info("Building executable with PyInstaller...")

        if not self.validate_spec_file():
            return False

        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",  # Clean cache
            "--noconfirm",  # Don't ask for confirmation
            "school_system.spec"
        ]

        if not self.run_command(cmd, "PyInstaller compilation"):
            return False

        # Verify the executable was created
        exe_path = self.dist_dir / "SchoolSystemManagement.exe"
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"✓ Executable created: {exe_path} ({exe_size:.1f} MB)")
            return True
        else:
            logger.error("Executable was not created")
            return False

    def build_installer(self):
        """Build the installer using Inno Setup."""
        if sys.platform != "win32":
            logger.info("Skipping installer creation (not on Windows)")
            return True

        if not self.inno_compiler:
            logger.warning("Inno Setup not found - skipping installer creation")
            logger.warning("Executable is ready in dist/ directory")
            return True

        logger.info("Building installer with Inno Setup...")

        if not self.validate_inno_script():
            return False

        # Run Inno Setup compiler
        cmd = [
            self.inno_compiler,
            "/O" + str(self.installer_output),
            "/F" + "SchoolSystemManagement_Setup",
            str(self.project_root / "installer.iss")
        ]

        if not self.run_command(cmd, "Inno Setup compilation"):
            return False

        # Verify installer was created
        installer_path = self.installer_output / "SchoolSystemManagement_Setup.exe"
        if installer_path.exists():
            installer_size = installer_path.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"✓ Installer created: {installer_path} ({installer_size:.1f} MB)")
            return True
        else:
            logger.error("Installer was not created")
            return False

    def create_build_summary(self, success):
        """Create a build summary."""
        summary = {
            "build_timestamp": datetime.now().isoformat(),
            "success": success,
            "platform": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable_created": (self.dist_dir / "SchoolSystemManagement.exe").exists(),
            "installer_created": (self.installer_output / "SchoolSystemManagement_Setup.exe").exists() if sys.platform == "win32" else None
        }

        summary_file = self.project_root / "build_summary.json"
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"✓ Build summary saved: {summary_file}")
        except Exception as e:
            logger.error(f"Failed to save build summary: {e}")

    def run(self):
        """Run the complete build process."""
        logger.info("=" * 60)
        logger.info("SCHOOL SYSTEM MANAGEMENT - INSTALLER BUILD")
        logger.info("=" * 60)

        success = True

        try:
            # Step 1: Check requirements
            if not self.check_requirements():
                return False

            # Step 2: Clean build directories
            self.clean_build_directories()

            # Step 3: Create version file
            if not self.create_version_file():
                success = False

            # Step 4: Build executable
            if not self.build_executable():
                success = False

            # Step 5: Build installer (if on Windows)
            if not self.build_installer():
                success = False

        except KeyboardInterrupt:
            logger.warning("Build interrupted by user")
            success = False
        except Exception as e:
            logger.error(f"Unexpected error during build: {e}")
            success = False

        # Create build summary
        self.create_build_summary(success)

        # Final status
        logger.info("=" * 60)
        if success:
            logger.info("✓ BUILD COMPLETED SUCCESSFULLY")
            logger.info("Executable available in: dist/SchoolSystemManagement.exe")
            if sys.platform == "win32" and self.inno_compiler:
                logger.info("Installer available in: installer_output/SchoolSystemManagement_Setup.exe")
        else:
            logger.error("✗ BUILD FAILED")
            logger.error("Check the log file for details: build_installer.log")
        logger.info("=" * 60)

        return success


def main():
    """Main entry point."""
    builder = InstallerBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()