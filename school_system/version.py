"""
Version management for School System Management.

This module provides version information and utilities for version management.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

# Application version information
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Application metadata
APP_NAME = "School System Management"
APP_AUTHOR = "School Management Solutions"
APP_DESCRIPTION = "Comprehensive school management system for managing students, books, teachers, and resources"

class VersionManager:
    """Manages application versioning and build information."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Determine project root from this file's location
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.version_file = project_root / "version.json"

    def get_current_version(self) -> str:
        """Get the current version string."""
        return __version__

    def get_version_info(self) -> tuple:
        """Get the version as a tuple (major, minor, patch)."""
        return __version_info__

    def bump_version(self, bump_type: str = "patch") -> str:
        """
        Bump the version number.

        Args:
            bump_type: Type of version bump ('major', 'minor', 'patch')

        Returns:
            New version string
        """
        global __version__, __version_info__

        major, minor, patch = __version_info__

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump_type: {bump_type}")

        new_version = f"{major}.{minor}.{patch}"
        new_version_info = (major, minor, patch)

        # Update the module-level variables
        __version__ = new_version
        __version_info__ = new_version_info

        # Update version file if it exists
        self.update_version_file()

        return new_version

    def update_version_file(self, build_info: Optional[Dict] = None) -> bool:
        """
        Update the version.json file with current version and build information.

        Args:
            build_info: Additional build information to include

        Returns:
            True if successful, False otherwise
        """
        import datetime
        import sys

        version_data = {
            "version": self.get_current_version(),
            "version_tuple": list(self.get_version_info()),
            "app_name": APP_NAME,
            "app_author": APP_AUTHOR,
            "app_description": APP_DESCRIPTION,
            "build_date": datetime.datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }

        if build_info:
            version_data.update(build_info)

        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_version_file(self) -> Optional[Dict]:
        """Load version information from version.json file."""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def get_full_version_info(self) -> Dict:
        """Get comprehensive version information."""
        version_data = self.load_version_file()

        if version_data:
            return version_data

        # Fallback to basic info
        return {
            "version": self.get_current_version(),
            "version_tuple": list(self.get_version_info()),
            "app_name": APP_NAME,
            "app_author": APP_AUTHOR,
            "app_description": APP_DESCRIPTION
        }

# Global version manager instance
version_manager = VersionManager()

def get_version() -> str:
    """Get the current application version."""
    return version_manager.get_current_version()

def get_app_info() -> Dict:
    """Get application information including version."""
    return version_manager.get_full_version_info()