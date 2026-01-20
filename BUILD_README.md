# School System Management - Build Guide

This guide explains how to build the School System Management application into a professional installer.

## Prerequisites

### Required Software
1. **Python 3.7 or higher**
   - Download from: https://python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Git** (for cloning the repository)
   - Download from: https://git-scm.com/downloads

### Optional Software (for complete installer)
3. **Inno Setup** (for creating the Windows installer)
   - Download from: https://jrsoftware.org/isinfo.php
   - Install the latest version (6.x recommended)

## Quick Start Build

### Windows (Simplest Method)
1. Open Command Prompt in the project directory
2. Run the build script:
   ```batch
   build_installer.bat
   ```
3. Wait for the build to complete
4. Find your files in:
   - `dist/SchoolSystemManagement.exe` (executable)
   - `installer_output/SchoolSystemManagement_Setup.exe` (installer)

### Manual Build Process

If you prefer to build manually or are on a different platform:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r build_requirements.txt
   ```

2. **Build the executable:**
   ```bash
   python -m PyInstaller --clean --noconfirm school_system.spec
   ```

3. **Create installer (Windows only):**
   ```bash
   # Requires Inno Setup to be installed
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

## Project Structure After Build

```
project_root/
├── dist/                          # PyInstaller output
│   └── SchoolSystemManagement.exe # Main executable
│   └── _internal/                 # Packed Python modules
├── build/                         # PyInstaller build files
├── installer_output/              # Inno Setup output
│   └── SchoolSystemManagement_Setup.exe
├── build_installer.log            # Build log
└── build_summary.json             # Build summary
```

## Configuration Files

### PyInstaller Spec File (`school_system.spec`)
- Defines what files to include
- Specifies hidden imports
- Configures the executable properties
- Includes icons, templates, and data files

### Inno Setup Script (`installer.iss`)
- Creates professional Windows installer
- Includes desktop shortcuts
- Registers file associations
- Handles uninstallation

## Troubleshooting

### Common Issues

#### 1. "Python not found" error
- Ensure Python is installed and in your PATH
- Try `python --version` in command prompt

#### 2. "PyInstaller not found" error
- Install PyInstaller: `pip install pyinstaller`
- Or run the batch file which handles this automatically

#### 3. "Inno Setup not found" warning
- This is normal if Inno Setup isn't installed
- You can still use the executable from `dist/` folder
- Install Inno Setup for professional installer creation

#### 4. Build fails with import errors
- Ensure all requirements are installed: `pip install -r requirements.txt`
- Check the build log: `build_installer.log`

#### 5. Executable is too large
- The executable includes all dependencies
- Size is normal for a PyQt6 application with all libraries
- UPX compression is enabled to reduce size

### Build Log Analysis
Check `build_installer.log` for detailed error information.

## Distribution

### Using the Installer (Recommended)
1. Run `SchoolSystemManagement_Setup.exe`
2. Follow the installation wizard
3. The application will be installed with:
   - Desktop shortcut
   - Start menu entry
   - Uninstaller in Control Panel

### Using the Executable Directly
1. Copy `SchoolSystemManagement.exe` to desired location
2. Copy the `_internal` folder (must be in same directory)
3. Run the executable

## Application Features

After installation, users can:

- **Login** with default credentials:
  - Username: `admin`
  - Password: `harry123`

- **Manage Students**: Add, edit, view student records
- **Manage Books**: Catalog and track library books
- **Manage Teachers**: Staff management system
- **Handle Borrowing**: Book checkout and return
- **Generate Reports**: Various analytics and reports
- **User Management**: Role-based access control

## Technical Details

### Included Files
- **Executable**: Standalone Windows application
- **Database**: SQLite database (created on first run)
- **Templates**: Excel templates for bulk import
- **Icons**: Application icons and resources
- **Themes**: Light/dark theme support

### System Requirements
- **OS**: Windows 7 SP1 or later (64-bit recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **Display**: 1024x768 minimum resolution

### Security Notes
- Database files are stored in user documents folder
- All passwords are hashed using industry-standard methods
- Audit logs track all administrative actions

## Support

For build issues or questions:
1. Check the build log files
2. Verify all prerequisites are installed
3. Ensure you're running from the project root directory

## Advanced Configuration

### Customizing the Build
Edit `school_system.spec` to:
- Add/remove hidden imports
- Include additional data files
- Change executable icon
- Modify compression settings

### Customizing the Installer
Edit `installer.iss` to:
- Change installation paths
- Add custom installation steps
- Modify shortcuts and file associations
- Add license agreements or documentation