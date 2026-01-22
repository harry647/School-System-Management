; Inno Setup Script for School System Management Application
; This script creates a professional installer with all necessary components

#include "version.iss"

#define MyAppName "School System Management"
#define MyAppPublisher "School Management Solutions"
#define MyAppURL "https://www.schoolmanagement.com"
#define MyAppExeName "SchoolSystemManagement.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".ssm"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{4A7B8C9D-1E2F-3G4H-5I6J-7K8L9M0N1O2P}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ChangesAssociations=yes
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=SchoolSystemManagement_Setup
SetupIconFile=school_system\gui\resources\icons\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable and all application files
Source: "dist\SchoolSystemManagement.exe"; DestDir: "{app}"; Flags: ignoreversion

; Data files and directories
Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Template files
Source: "book_import_template.xlsx"; DestDir: "{app}"; Flags: ignoreversion
Source: "student_import_template.xlsx"; DestDir: "{app}"; Flags: ignoreversion

; Documentation (create if exists)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; VC++ Redistributables (if needed)
; Source: "vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedistNeedsInstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppString}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Register file associations
Root: HKCR; Subkey: "{#MyAppAssocExt}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocKey}"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; Add application to PATH (optional)
; Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: IsAdminInstallMode

[Code]
// Global variables
var
  DataDirPage: TInputDirWizardPage;
  ConfigFile: String;

function InitializeSetup(): Boolean;
begin
  // Check for existing installation
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1') then
  begin
    if MsgBox('{#MyAppName} is already installed. Do you want to continue with the installation?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;

  // Check for .NET Framework (if needed)
  // if not IsDotNetInstalled(net4full, 0) then
  // begin
  //   MsgBox('{#MyAppName} requires Microsoft .NET Framework 4.0 or later. Please install it and run this setup again.', mbInformation, MB_OK);
  //   Result := False;
  //   Exit;
  // end;

  Result := True;
end;

procedure InitializeWizard();
begin
  // Create custom page for data directory selection
  DataDirPage := CreateInputDirPage(
    wpSelectDir,
    'Select Data Directory',
    'Where should {#MyAppName} store its data files?',
    'Please select a directory where {#MyAppName} will store its database and configuration files.',
    False,
    ''
  );

  // Set default data directory
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{userdocs}\{#MyAppName}');

  // Set config file path
  ConfigFile := ExpandConstant('{app}\school_system\config.json');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = DataDirPage.ID then
  begin
    // Validate data directory
    if DataDirPage.Values[0] = '' then
    begin
      MsgBox('Please select a data directory.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    // Check if directory is writable
    if not DirExists(DataDirPage.Values[0]) then
    begin
      if not CreateDir(DataDirPage.Values[0]) then
      begin
        MsgBox('Cannot create the selected data directory. Please choose a different location.', mbError, MB_OK);
        Result := False;
        Exit;
      end;
    end;
  end;

  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Update configuration file with data directory
    if FileExists(ConfigFile) then
    begin
      // Note: In a real implementation, you would update the JSON config file
      // with the selected data directory path
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  case CurUninstallStep of
    usUninstall:
    begin
      // Optionally remove data directory (ask user first)
      DataDir := ExpandConstant('{userdocs}\{#MyAppName}');
      if DirExists(DataDir) then
      begin
        if MsgBox('Do you want to remove all application data?', mbConfirmation, MB_YESNO) = IDYES then
        begin
          DelTree(DataDir, True, True, True);
        end;
      end;
    end;
  end;
end;

// Function to check if VC++ Redistributables are needed
function VCRedistNeedsInstall(): Boolean;
begin
  // Check if VC++ 2015-2022 Redistributables are installed
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
  if not Result then
  begin
    Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
  end;
end;

// Function to check admin install mode
function IsAdminInstallMode(): Boolean;
begin
  Result := IsAdminLoggedOn;
end;