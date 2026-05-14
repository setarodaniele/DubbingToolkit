[Setup]
AppName=Dubbing Toolkit
AppVersion=0.1
DefaultDirName={pf}\DubbingToolkit
DefaultGroupName=Dubbing Toolkit
OutputDir=output
OutputBaseFilename=setup_dubbing_toolkit
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\build_payload\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Dubbing Toolkit"; Filename: "{app}\StartDubbing.bat"
Name: "{commondesktop}\Dubbing Toolkit"; Filename: "{app}\StartDubbing.bat"

[Run]
Filename: "{app}\StartDubbing.bat"; Description: "Avvia Dubbing Toolkit"; Flags: nowait postinstall