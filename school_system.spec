# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller specification file for School System Management Application.

This file defines how to build the application executable with all necessary
dependencies, data files, and resources included.
"""

import os
import sys
from pathlib import Path

# Get the project root directory
import os
project_root = Path(os.path.abspath("."))

# Define data files to include
data_files = [
    # Configuration files
    ('school_system/config.json', 'school_system/'),

    # GUI resources (icons, themes, templates)
    ('school_system/gui/resources/icons/*.png', 'school_system/gui/resources/icons/'),
    ('school_system/gui/resources/styles/*.qss', 'school_system/gui/resources/styles/'),
    ('school_system/gui/resources/templates/*.html', 'school_system/gui/resources/templates/'),

    # Data directories (create empty if needed)
    ('school_system/data', 'school_system/data'),
    ('school_system/data/backup', 'school_system/data/backup'),
    ('school_system/data/exports', 'school_system/data/exports'),

    # Include any additional resource files
    ('book_import_template.xlsx', '.'),
    ('student_import_template.xlsx', '.'),
]

# Define hidden imports (modules that PyInstaller might miss)
hidden_imports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport',

    # Standard library modules used dynamically
    'sqlite3',
    'hashlib',
    'json',
    'csv',
    'logging',
    'datetime',
    'os',
    'sys',
    'pathlib',
    'typing',
    'contextlib',

    # Third-party modules
    'pandas',
    'openpyxl',
    'fpdf',
    'qrcode',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',

    # All school_system modules to ensure complete inclusion
    'school_system',
    'school_system.config',
    'school_system.config.database',
    'school_system.config.logging',
    'school_system.config.settings',
    'school_system.core',
    'school_system.core.exceptions',
    'school_system.core.utils',
    'school_system.core.validators',
    'school_system.database',
    'school_system.database.connection',
    'school_system.database.repositories',
    'school_system.database.repositories.base',
    'school_system.database.repositories.user_repo',
    'school_system.database.repositories.student_repo',
    'school_system.database.repositories.teacher_repo',
    'school_system.database.repositories.book_repo',
    'school_system.database.repositories.furniture_repo',
    'school_system.database.repositories.session_repo',
    'school_system.database.repositories.audit_log_repo',
    'school_system.database.repositories.user_activity_repo',
    'school_system.database.migrations',
    'school_system.gui',
    'school_system.gui.base',
    'school_system.gui.base.widgets',
    'school_system.gui.dialogs',
    'school_system.gui.resources',
    'school_system.gui.windows',
    'school_system.models',
    'school_system.services',
    'school_system.src',
    'school_system.utils',
]

# Define binaries (DLLs, shared libraries)
binaries = []

# Define excludes (modules to exclude to reduce size)
excludes = [
    # Exclude unused standard library modules
    'tkinter',  # We use PyQt6, not tkinter
    'unittest',  # Not needed in production
    'pdb',  # Python debugger
    'pydoc',  # Documentation generator

    # Exclude third-party modules we don't use
    'numpy',  # Not used
    'matplotlib',  # Not used
    'scipy',  # Not used
]

# Define the main application entry point
main_script = 'run_school_system.py'

# PyInstaller Analysis
a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary files to reduce executable size
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SchoolSystemManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='school_system/gui/resources/icons/logo.png',  # Application icon
    version_file=None,
)