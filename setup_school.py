# setup_school.py

import PyInstaller.__main__
import os
import subprocess
import sys
import shutil
import tkinter as tk
from tkinter import messagebox

def package_program(script_path, icon_path=None, name=None, additional_files=None, hidden_imports=None, windowed=True, use_venv=True):
    """
    Packages the Python script into an executable and prepares it for Inno Setup using SQLite.
    """
    # Use virtual environment if specified
    if use_venv:
        venv_dir = "C:\\Users\\USER\\Desktop\\SchoolVenv"
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe") if os.name == 'nt' else os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe") if os.name == 'nt' else os.path.join(venv_dir, "bin", "pip")

        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment in {venv_dir}...")
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

        print("Installing/Updating requirements in venv...")
        subprocess.run([venv_pip, "install", "-r", "requirements.txt", "--upgrade"], check=True)

        pyinstaller_python = venv_python
    else:
        pyinstaller_python = sys.executable

    # Paths for Tcl/Tk libraries
    tcl_path = "C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tcl8.6"
    tk_path = "C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tk8.6"

    # Build PyInstaller arguments
    pyinstaller_args = [
        script_path,
        "--onefile",
        "--noupx",
        "--clean",
    ]

    if windowed:
        pyinstaller_args.append("--windowed")
    if name:
        pyinstaller_args.extend(["--name", name])
    if icon_path:
        pyinstaller_args.extend(["--icon", icon_path])

    separator = ";" if os.name == "nt" else ":"
    if os.path.exists(tcl_path) and os.path.exists(tk_path):
        pyinstaller_args.extend(["--add-data", f"{tcl_path}{separator}tcl8.6"])
        pyinstaller_args.extend(["--add-data", f"{tk_path}{separator}tk8.6"])
    else:
        raise FileNotFoundError("Tcl/Tk libraries missing.")

    # Ensure required files are included
    required_files = additional_files or []
    if "config.json" not in [os.path.basename(f) for f in required_files]:
        required_files.append("config.json")

    for file_path in required_files:
        if os.path.exists(file_path):
            pyinstaller_args.extend(["--add-data", f"{file_path}{separator}."])
        else:
            print(f"Warning: File {file_path} not found, skipping.")

    if hidden_imports:
        for module in hidden_imports:
            pyinstaller_args.extend(["--hidden-import", module])

    output_dir = "C:\\Users\\USER\\Desktop\\SchoolOutput"
    pyinstaller_args.extend(["--distpath", output_dir])

    print("PyInstaller command:", " ".join([pyinstaller_python, "-m", "PyInstaller"] + pyinstaller_args))

    print("Running PyInstaller...")
    PyInstaller.__main__.run(pyinstaller_args)
    print("PyInstaller completed successfully!")

    try:
        # Prepare files for Inno Setup
        staging_dir = "C:\\Users\\USER\\Desktop\\SchoolInnoStaging"
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir)
        os.makedirs(staging_dir)

        exe_name = name + (".exe" if os.name == "nt" else "")
        exe_path = os.path.join(output_dir, exe_name)
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Executable {exe_path} not found. Ensure PyInstaller has run successfully.")

        shutil.copy(exe_path, staging_dir)
        for file in required_files:
            if os.path.exists(file):
                shutil.copy(file, staging_dir)
            else:
                print(f"Warning: File {file} not found, skipping.")
        if icon_path and os.path.exists(icon_path):
            shutil.copy(icon_path, staging_dir)

        # Create Inno Setup script (no MySQL-related tasks)
        inno_script = os.path.join(staging_dir, "setup.iss")
        with open(inno_script, "w") as f:
            f.write("""
[Setup]
AppName=HarLuFran InnoFlux SMS
AppVersion=1.0.01
DefaultDirName={commonpf}\\HarLuFran InnoFlux SMS
DefaultGroupName=HarLuFran InnoFlux SMS
OutputDir=C:\\Users\\USER\\Desktop\\SchoolInstallerOutput
OutputBaseFilename=HarLuFranInnoFluxSMSSetup
SetupIconFile=school_icon.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\\HarLuFranInnoFluxSMS.exe

[Languages]
Name: english; MessagesFile: compiler:Default.isl

[Files]
Source: "C:\\Users\\USER\\Desktop\\SchoolInnoStaging\\HarLuFranInnoFluxSMS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\\Users\\USER\\Desktop\\SchoolInnoStaging\\licence.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\\Users\\USER\\Desktop\\SchoolInnoStaging\\renewal.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\HarLuFran InnoFlux SMS"; Filename: "{app}\\HarLuFranInnoFluxSMS.exe"
Name: "{group}\\Uninstall HarLuFran InnoFlux SMS"; Filename: "{uninstallexe}"
Name: "{userdesktop}\\HarLuFran InnoFlux SMS"; Filename: "{app}\\HarLuFranInnoFluxSMS.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\\HarLuFranInnoFluxSMS.exe"; Description: "Launch HarLuFran InnoFlux SMS"; Flags: nowait postinstall skipifsilent

[Code]
const
  WM_WININICHANGE = $001A;

function FindWindow(lpClassName, lpWindowName: String): Integer;
  external 'FindWindowW@user32.dll stdcall';

function MyErrorMessage(Msg: String): Integer;
begin
  Result := MsgBox(Msg, mbError, MB_OK);
end;

function CheckForRunningApp(): Boolean;
var
  hWindow: Integer;
begin
  hWindow := FindWindow('', 'HarLuFran InnoFlux SMS');
  Result := (hWindow <> 0);
  if Result then
  begin
    MsgBox('The application is currently running. Please close it before proceeding.', mbError, MB_OK);
  end;
end;

function NeedRestart(): Boolean;
begin
  Result := CheckForRunningApp();
end;

function IsUpgrade(): Boolean;
var
  Version: String;
begin
  Result := False;
  if RegQueryStringValue(HKLM, 'Software\\HarLuFran InnoFlux SMS', 'Version', Version) then
  begin
    Result := True;
  end;
end;

function InitializeSetup(): Boolean;
var
  Msg: String;
begin
  if IsUpgrade() then
  begin
    Msg := 'A previous version of HarLuFran InnoFlux SMS is already installed. It is recommended to uninstall it before proceeding with this installation.';
    MsgBox(Msg, mbInformation, MB_OK);
  end;

  if NeedRestart() then
  begin
    Result := False;
    Exit;
  end;

  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    Log('Starting installation process...');
  end;

  if CurStep = ssPostInstall then
  begin
    Log('Post-installation steps completed.');
  end;
end;

procedure DeinitializeSetup();
begin
  Log('Installation process finished.');
end;

function InitializeUninstall(): Boolean;
begin
  Log('Uninstallation process starting...');
  Result := True;
end;

procedure DeinitializeUninstall();
begin
  Log('Uninstallation process finished.');
end;
            """)

        # Run Inno Setup compiler
        inno_compiler = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
        if not os.path.exists(inno_compiler):
            raise FileNotFoundError("Inno Setup compiler not found. Please install Inno Setup.")
        if icon_path and not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file '{icon_path}' not found.")

        print("Compiling Inno Setup installer...")
        subprocess.run([inno_compiler, inno_script], check=True)
        print("Installer created at C:\\Users\\USER\\Desktop\\SchoolInstallerOutput\\HarLuFranInnoFluxSMSSetup.exe")
        messagebox.showinfo("Success", "Installer created at C:\\Users\\USER\\Desktop\\SchoolInstallerOutput\\HarLuFranInnoFluxSMSSetup.exe")

    except Exception as e:
        print(f"Packaging failed: {e}")
        messagebox.showerror("Packaging Error", f"Failed to package the application: {e}")
        raise

if __name__ == "__main__":
    script_path = "main.py"
    icon_path = "school_icon.ico"
    name = "HarLuFranInnoFluxSMS"
    additional_files_to_include = [
        "library_logic.py",
        "db_utils.py",
        "QRcode_Reader.py",
        "db_manager.py",
        "gui_manager.py",
        "licence.json",
        "renewal.json",
        "help.txt",
        
    ]
    hidden_imports = [
        "requests",
        "pandas",
        "openpyxl",
        "qrcode",
        "PIL",
        "PIL.Image",
        "reportlab",
        "reportlab.lib.pagesizes",
        "reportlab.pdfgen",
        "pdf2image",
        "cryptography",
        "cryptography.fernet",
        "cryptography.hazmat.primitives",
        "cryptography.hazmat.primitives.kdf.pbkdf2",
        "pyserial",
        "speech_recognition",
        "sounddevice",
        "schedule",
        "boto3",
        "tkinter",
    ]

    package_program(
        script_path,
        icon_path=icon_path,
        name=name,
        additional_files=additional_files_to_include,
        hidden_imports=hidden_imports,
        windowed=True,
        use_venv=True
    )