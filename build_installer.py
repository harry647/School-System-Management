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
            logger.info(f"[SUCCESS] {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] {description} failed")
            logger.error(f"Error code: {e.returncode}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error in {description}: {e}")
            return False

    def check_requirements(self):
        """Check if all required tools and dependencies are available."""
        logger.info("Checking build requirements...")

        # Check if running in virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.warning("Not running in a virtual environment. This may cause issues with the build.")
            logger.warning("The build script should be run from the build_installer.bat file which sets up the venv.")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 7):
            logger.error(f"Python {python_version.major}.{python_version.minor} is not supported. Need Python 3.7+")
            return False
        logger.info(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")

        # Check if PyInstaller is installed
        try:
            import PyInstaller
            logger.info(f"[OK] PyInstaller {PyInstaller.__version__} is available")
        except ImportError:
            logger.error("PyInstaller is not installed in the virtual environment.")
            logger.error("Make sure to run build_installer.bat which sets up the venv with all requirements.")
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
                logger.info(f"[OK] Inno Setup found at: {self.inno_compiler}")
            else:
                logger.warning("Inno Setup not found. Install from: https://jrsoftware.org/isinfo.php")
                logger.warning("You can still build the executable, but not the installer")
        else:
            logger.info("Non-Windows platform detected - skipping Inno Setup check")

        # Check if required packages are installed
        # Format: (import_name, display_name)
        required_packages = [
            ('PyQt6', 'PyQt6'),
            ('pandas', 'pandas'),
            ('openpyxl', 'openpyxl'),
            ('fpdf', 'fpdf'),
            ('qrcode', 'qrcode'),
            ('PIL', 'Pillow')
        ]

        missing_packages = []
        for import_name, display_name in required_packages:
            try:
                __import__(import_name)
                logger.info(f"[OK] {display_name} is available")
            except ImportError:
                missing_packages.append(display_name)

        if missing_packages:
            logger.error(f"Missing required packages in virtual environment: {', '.join(missing_packages)}")
            logger.error("The build script should have installed all requirements automatically.")
            logger.error("Try deleting the 'build_venv' folder and running build_installer.bat again.")
            logger.error("If the problem persists, manually install missing packages:")
            for package in missing_packages:
                if package == "Pillow":
                    logger.error(f"  pip install {package}")
                else:
                    logger.error(f"  pip install {package}")
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
                    logger.info(f"[OK] Cleaned {dir_path}")
                except Exception as e:
                    logger.warning(f"Could not clean {dir_path}: {e}")

    def validate_spec_file(self):
        """Validate that the PyInstaller spec file exists and is valid."""
        spec_file = self.project_root / "school_system.spec"
        if not spec_file.exists():
            logger.error(f"Spec file not found: {spec_file}")
            return False

        logger.info(f"[OK] Spec file found: {spec_file}")
        return True

    def validate_inno_script(self):
        """Validate that the Inno Setup script exists."""
        inno_script = self.project_root / "installer.iss"
        if not inno_script.exists():
            logger.error(f"Inno Setup script not found: {inno_script}")
            return False

        logger.info(f"[OK] Inno Setup script found: {inno_script}")
        return True

    def create_version_file(self):
        """Create version information file using the version manager."""
        try:
            # Import version manager
            sys.path.insert(0, str(self.project_root))
            from school_system.version import version_manager

            # Update version file with build information
            build_info = {
                "build_type": "installer",
                "build_platform": sys.platform,
            }

            success = version_manager.update_version_file(build_info)
            if success:
                logger.info(f"[SUCCESS] Created/updated version file: {version_manager.version_file}")

                # Generate Inno Setup version file
                version_iss_file = self.project_root / "version.iss"
                try:
                    with open(version_iss_file, 'w') as f:
                        f.write(f'# Version definitions for Inno Setup\n')
                        f.write(f'# This file is generated during the build process\n\n')
                        f.write(f'#define MyAppVersion "{version_manager.get_current_version()}"\n')
                        f.write(f'#define MyAppVersionInfo VersionToInt(MyAppVersion)\n')
                    logger.info(f"[SUCCESS] Generated Inno Setup version file: {version_iss_file}")
                except Exception as e:
                    logger.warning(f"Failed to generate version.iss file: {e}")

                return True
            else:
                logger.error("Failed to update version file")
                return False

        except Exception as e:
            logger.error(f"Failed to create version file: {e}")
            return False

    def convert_icons(self):
        """Convert PNG icons to ICO format for Windows compatibility."""
        logger.info("Converting icons to ICO format...")

        try:
            # Import PIL here to avoid issues if not installed during early checks
            from PIL import Image
        except ImportError:
            logger.error("Pillow not available for icon conversion")
            return False

        icon_conversions = [
            {
                'png': self.project_root / 'school_system' / 'gui' / 'resources' / 'icons' / 'logo.png',
                'ico': self.project_root / 'school_system' / 'gui' / 'resources' / 'icons' / 'logo.ico',
                'sizes': [16, 32, 48, 64, 128, 256]
            }
        ]

        success_count = 0
        for conv in icon_conversions:
            if conv['png'].exists():
                try:
                    # Open and convert PNG to ICO
                    img = Image.open(conv['png'])
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')

                    icons = []
                    for size in conv['sizes']:
                        resized = img.resize((size, size), Image.Resampling.LANCZOS)
                        icons.append(resized)

                    # Save as ICO
                    icons[0].save(
                        conv['ico'],
                        format='ICO',
                        sizes=[(icon.size[0], icon.size[1]) for icon in icons],
                        append_images=icons[1:]
                    )

                    logger.info(f"[SUCCESS] Converted {conv['png'].name} to ICO with {len(conv['sizes'])} sizes")
                    success_count += 1

                except Exception as e:
                    logger.error(f"Failed to convert {conv['png']}: {e}")
            else:
                logger.warning(f"Source PNG not found: {conv['png']}")

        if success_count == len(icon_conversions):
            logger.info("[SUCCESS] All icons converted successfully")
            return True
        else:
            logger.error(f"Icon conversion incomplete: {success_count}/{len(icon_conversions)} converted")
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
            logger.info(f"[OK] Executable created: {exe_path} ({exe_size:.1f} MB)")
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
            logger.info(f"[OK] Installer created: {installer_path} ({installer_size:.1f} MB)")
            return True
        else:
            logger.error("Installer was not created")
            return False

    def create_distribution_zip(self):
        """Create a zip archive of all distribution files for easy transport."""
        logger.info("Creating distribution zip archive...")

        try:
            import zipfile
        except ImportError:
            logger.error("zipfile module not available")
            return False

        # Get version for zip filename
        try:
            from school_system.version import version_manager
            version = version_manager.get_current_version()
        except ImportError:
            version = "1.0.0"

        zip_filename = f"SchoolSystemManagement_v{version}_distribution.zip"
        zip_path = self.project_root / zip_filename

        # Files and directories to include
        include_files = [
            # Executable and internal files
            ("dist/SchoolSystemManagement.exe", "SchoolSystemManagement.exe"),
            ("dist/_internal", "_internal"),

            # Template files
            ("book_import_template.xlsx", "book_import_template.xlsx"),
            ("student_import_template.xlsx", "student_import_template.xlsx"),

            # Documentation
            ("README.md", "README.md"),
            ("LICENSE.txt", "LICENSE.txt"),
            ("BUILD_README.md", "BUILD_README.md"),

            # Version information
            ("version.json", "version.json"),
        ]

        # Add installer if it exists
        installer_path = self.installer_output / "SchoolSystemManagement_Setup.exe"
        if installer_path.exists():
            include_files.append((str(installer_path), "SchoolSystemManagement_Setup.exe"))

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source, arcname in include_files:
                    source_path = self.project_root / source

                    if source_path.is_file():
                        # Add single file
                        zipf.write(source_path, arcname)
                        logger.info(f"Added file: {arcname}")
                    elif source_path.is_dir():
                        # Add directory recursively
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                # Calculate relative path for archive
                                rel_path = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, str(rel_path))
                        logger.info(f"Added directory: {arcname}")
                    else:
                        logger.warning(f"Source not found: {source_path}")

                # Create a distribution README
                dist_readme_content = f"""# School System Management v{version}

This archive contains the complete School System Management application.

## Contents
- SchoolSystemManagement.exe - Main application executable
- _internal/ - Application dependencies (required)
- book_import_template.xlsx - Book import template
- student_import_template.xlsx - Student import template
- README.md - Application documentation
- LICENSE.txt - License information

## Installation
1. Extract all files to a folder on your computer
2. Run SchoolSystemManagement.exe
3. The application will create its database automatically on first run

## System Requirements
- Windows 7 SP1 or later (64-bit recommended)
- 2GB RAM minimum, 4GB recommended
- 500MB free disk space

## Default Login Credentials
- Username: admin
- Password: harry123

## Support
For issues or questions, refer to the README.md file.

Built on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: {version}
"""

                zipf.writestr("DISTRIBUTION_README.md", dist_readme_content)
                logger.info("Added distribution README")

            # Get zip file size
            zip_size = zip_path.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"[SUCCESS] Created distribution zip: {zip_path} ({zip_size:.1f} MB)")
            return True

        except Exception as e:
            logger.error(f"Failed to create distribution zip: {e}")
            return False

    def create_build_summary(self, success):
        """Create a build summary."""
        # Check if running in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

        # Check if zip was created
        zip_created = False
        try:
            from school_system.version import version_manager
            version = version_manager.get_current_version()
            zip_file = self.project_root / f"SchoolSystemManagement_v{version}_distribution.zip"
            zip_created = zip_file.exists()
        except:
            zip_created = False

        summary = {
            "build_timestamp": datetime.now().isoformat(),
            "success": success,
            "platform": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "virtual_environment": in_venv,
            "executable_created": (self.dist_dir / "SchoolSystemManagement.exe").exists(),
            "installer_created": (self.installer_output / "SchoolSystemManagement_Setup.exe").exists() if sys.platform == "win32" else None,
            "distribution_zip_created": zip_created
        }

        summary_file = self.project_root / "build_summary.json"
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"[OK] Build summary saved: {summary_file}")
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

            # Step 3: Convert icons
            if not self.convert_icons():
                success = False

            # Step 4: Create version file
            if not self.create_version_file():
                success = False

            # Step 5: Build executable
            if not self.build_executable():
                success = False

            # Step 6: Build installer (if on Windows)
            if not self.build_installer():
                success = False

            # Step 7: Create distribution zip
            if not self.create_distribution_zip():
                logger.warning("Distribution zip creation failed, but build may still be usable")

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
            logger.info("[SUCCESS] BUILD COMPLETED SUCCESSFULLY")
            logger.info("Executable available in: dist/SchoolSystemManagement.exe")
            if sys.platform == "win32" and self.inno_compiler:
                logger.info("Installer available in: installer_output/SchoolSystemManagement_Setup.exe")

            # Check if zip was created
            try:
                from school_system.version import version_manager
                version = version_manager.get_current_version()
                zip_file = f"SchoolSystemManagement_v{version}_distribution.zip"
                if (self.project_root / zip_file).exists():
                    logger.info(f"Distribution zip available: {zip_file}")
            except:
                logger.info("Distribution zip should be available in project root")

            logger.info("Build was performed in isolated virtual environment for consistency.")
        else:
            logger.error("[ERROR] BUILD FAILED")
            logger.error("Check the log file for details: build_installer.log")
            logger.info("Virtual environment 'build_venv' remains available for debugging.")
        logger.info("=" * 60)

        return success


def main():
    """Main entry point."""
    builder = InstallerBuilder()
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()