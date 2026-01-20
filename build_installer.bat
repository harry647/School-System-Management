@echo off
REM Batch script to build the School System Management installer
REM This script handles all the necessary steps for creating a professional installer

echo ========================================
echo SCHOOL SYSTEM MANAGEMENT INSTALLER BUILD
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and make sure it's in your PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "run_school_system.py" (
    echo ERROR: Please run this script from the project root directory
    echo The script should be in the same directory as run_school_system.py
    pause
    exit /b 1
)

echo Checking Python version...
python -c "import sys; v=sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro}'); sys.exit(0 if v >= (3,7) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.7 or higher is required
    pause
    exit /b 1
)

echo Python version check passed.
echo.

REM Install/upgrade PyInstaller if needed
echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if Inno Setup is available
echo Checking for Inno Setup...
set "INNO_FOUND="
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    "C:\Program Files\Inno Setup 5\ISCC.exe"
) do (
    if exist %%p (
        set "INNO_FOUND=%%p"
        goto :inno_found
    )
)

:inno_found
if defined INNO_FOUND (
    echo Inno Setup found at: %INNO_FOUND%
) else (
    echo WARNING: Inno Setup not found.
    echo You can still build the executable, but not the installer.
    echo Download Inno Setup from: https://jrsoftware.org/isinfo.php
    echo.
)

REM Create necessary directories
if not exist "installer_output" mkdir installer_output

REM Run the build script
echo.
echo Starting build process...
echo This may take several minutes...
echo.

python build_installer.py
set BUILD_RESULT=%errorlevel%

echo.
if %BUILD_RESULT% equ 0 (
    echo ========================================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Your files are ready:
    echo - Executable: dist\SchoolSystemManagement.exe
    if defined INNO_FOUND (
        echo - Installer: installer_output\SchoolSystemManagement_Setup.exe
        echo.
        echo To install: Run the installer executable and follow the setup wizard.
    ) else (
        echo.
        echo NOTE: No installer created (Inno Setup not found)
        echo You can distribute the executable directly.
    )
    echo.
    echo Default login credentials:
    echo   Username: admin
    echo   Password: harry123
    echo.
) else (
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo.
    echo Check the following files for details:
    echo - build_installer.log
    echo - build_summary.json
    echo.
)

pause
exit /b %BUILD_RESULT%