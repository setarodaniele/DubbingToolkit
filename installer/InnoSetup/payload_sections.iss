[Files]
Source: "..\build_payload\Tools\*"; DestDir: "{app}\Tools"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\core\*"; DestDir: "{app}\core"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\locale\*"; DestDir: "{app}\locale"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\ps\*"; DestDir: "{app}\ps"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Scripts\*"; DestDir: "{app}\Scripts"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Settings\*"; DestDir: "{app}\Settings"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\Docs\*"; DestDir: "{app}\Docs"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\build_payload\StartDubbing.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build_payload\Billing\tts_voices_cost.json"; DestDir: "{app}\Billing"; Flags: ignoreversion
Source: "..\build_payload\credentials\azure_speech_credentials.template.json"; DestDir: "{app}\credentials"; Flags: ignoreversion
Source: "..\build_payload\credentials\google_speech_credentials.template.json"; DestDir: "{app}\credentials"; Flags: ignoreversion
Source: "..\build_payload\credentials\README.md"; DestDir: "{app}\credentials"; Flags: ignoreversion
Source: "assets\DubbingToolkit_Studio.ico";    DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\DubbingToolkit_Workspace.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Dirs]
Name: "{app}\Workspace"
Name: "{app}\credentials"
Name: "{app}\Audio_Input"
Name: "{app}\Audio_Extracted"
Name: "{app}\Dubbed"
Name: "{app}\Output"
Name: "{app}\Transcripts"
Name: "{app}\Translated"
Name: "{app}\Video_Input"
Name: "{app}\Logs"
Name: "{app}\Billing"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Installation"
Type: filesandordirs; Name: "{app}\Tools"
Type: filesandordirs; Name: "{app}\core"
Type: filesandordirs; Name: "{app}\locale"
Type: filesandordirs; Name: "{app}\ps"
Type: filesandordirs; Name: "{app}\Scripts"
Type: filesandordirs; Name: "{app}\Settings"
Type: filesandordirs; Name: "{app}\Docs"
Type: filesandordirs; Name: "{app}\Workspace"
Type: files;          Name: "{app}\StartDubbing.bat"
Type: files;          Name: "{app}\Billing\tts_voices_cost.json"
Type: files;          Name: "{app}\credentials\azure_speech_credentials.template.json"
Type: files;          Name: "{app}\credentials\google_speech_credentials.template.json"
Type: files;          Name: "{app}\credentials\README.md"
