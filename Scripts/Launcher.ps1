# ==================================================================
# Launcher.ps1 - LAUNCH AUTOMATIC DUBBING PROJECT
# ==================================================================


# --------------------------------------------------
# Force UTF-8 encoding for proper display of accented characters
# --------------------------------------------------
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Clear-Host

# --------------------------------------------------
# Core paths (must exist before anything else)
# --------------------------------------------------
$ScriptRoot = $PSScriptRoot
$RootFolder = Split-Path $ScriptRoot -Parent
$InstallationRoot = $RootFolder


# --------------------------------------------------
# Splash screen / project introduction
# --------------------------------------------------
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "         DUBBING TOOLKIT PROJECT          " -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "Author: Daniele" -ForegroundColor Green
Write-Host "Version: 1.0" -ForegroundColor Green
Write-Host "This tool automates video transcription" -ForegroundColor Yellow
Write-Host "and dubbing for tutorial projects." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# --------------------------------------------------
# Display which PowerShell is being used
# --------------------------------------------------
$PSInfo = if ($PSVersionTable.PSEdition -eq "Core") { "PowerShell 7" } else { "Windows PowerShell 5.1" }
Write-Host "[INFO] Running on $PSInfo" -ForegroundColor Magenta
Write-Host ""

# Optional: automatically set code page to UTF-8 if running in Windows PowerShell
try {
    if ($PSVersionTable.PSEdition -eq "Desktop") { chcp 65001 | Out-Null }
} catch { }

# --------------------------------------------------
# Logs folder management + keep last 10 logs
# --------------------------------------------------
$LogFolder = Join-Path $RootFolder 'Logs'
if (-not (Test-Path $LogFolder)) { New-Item -ItemType Directory -Path $LogFolder | Out-Null }

$Timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$LogFile = Join-Path $LogFolder "${Timestamp}_launcher.log"

$CutoffDate = (Get-Date).AddDays(-30)
Get-ChildItem -Path $LogFolder -Filter "*_launcher.log" | Where-Object { $_.LastWriteTime -lt $CutoffDate } | ForEach-Object { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }

Start-Transcript -Path $LogFile -Append -ErrorAction SilentlyContinue | Out-Null

# --------------------------------------------------
# Dynamic language selection
# --------------------------------------------------
$DefaultSettingFile     = Join-Path $RootFolder 'Settings\settings_default.json'
$PersistentSettingFile  = Join-Path $RootFolder 'Settings\settings_persistent.json'
$DefaultSettings        = Get-Content $DefaultSettingFile -Encoding UTF8 | ConvertFrom-Json
$DefaultLang            = $DefaultSettings.interface_lang

$LocaleFolder = Join-Path $RootFolder 'Locale'
$SystemFolder = Join-Path $LocaleFolder 'System'
$ActiveFolder = Join-Path $LocaleFolder 'Active'
$LanguageFile = Join-Path $SystemFolder 'languages.json'

if (-not (Test-Path $LanguageFile)) {
    Write-Host "[ERROR] languages.json not found: $LanguageFile" -ForegroundColor Red
    exit 1
}

$LanguagesMap   = Get-Content $LanguageFile -Encoding UTF8 | ConvertFrom-Json
$AvailableLangs = @()
foreach ($key in $LanguagesMap.PSObject.Properties.Name) {
    if ($key -match '_comment$') { continue }
    if (Test-Path (Join-Path $ActiveFolder "$key.json")) { $AvailableLangs += $key }
}

# Check if language was preset by installer via settings_persistent.json
$LangPresetByInstaller = $false
if (Test-Path $PersistentSettingFile) {
    $Persistent = Get-Content $PersistentSettingFile -Encoding UTF8 | ConvertFrom-Json
    if ($Persistent.language_preset_from_installer -eq $true -and
        $AvailableLangs -contains $Persistent.interface_lang) {
        $LangPresetByInstaller = $true
        $interface_langKey     = $Persistent.interface_lang
    }
}

if ($LangPresetByInstaller) {
    $MessagesFile = Join-Path $ActiveFolder "$interface_langKey.json"
    $Messages     = Get-Content $MessagesFile -Encoding UTF8 | ConvertFrom-Json
    $ReadableLang = $LanguagesMap.$interface_langKey
    Write-Host ($Messages.Launcher_LangFromInstaller -f $ReadableLang) -ForegroundColor Green
    Write-Host $Messages.Launcher_LangChangeHint -ForegroundColor Cyan
} else {
    # Normal flow — show language selection menu
    if ($AvailableLangs -contains $DefaultLang) {
        $selection = $AvailableLangs.IndexOf($DefaultLang) + 1
    } else { $selection = 1 }

    Write-Host "`nSelect language:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $AvailableLangs.Count; $i++) {
        Write-Host "$($i+1)) $($LanguagesMap.$($AvailableLangs[$i]))"
    }
    do {
        $inputSel = Read-Host "Enter the number corresponding to your language (press Enter for default: $DefaultLang)"
        if (-not [string]::IsNullOrWhiteSpace($inputSel)) { $selection = $inputSel }
    } while (-not ($selection -as [int]) -or $selection -lt 1 -or $selection -gt $AvailableLangs.Count)

    $interface_langKey = $AvailableLangs[$selection - 1]
    $MessagesFile      = Join-Path $ActiveFolder "$interface_langKey.json"
    $Messages          = Get-Content $MessagesFile -Encoding UTF8 | ConvertFrom-Json
    $ReadableLang      = $LanguagesMap.$interface_langKey
    Write-Host ($Messages.LanguageSelected -f $ReadableLang) -ForegroundColor Green
}

# --------------------------------------------------
# Checkpoint 0: Antivirus containment check
# --------------------------------------------------
Write-Host $Messages.Checkpoint0 -ForegroundColor Blue
Write-Host $Messages.Checkpoint0Warning -ForegroundColor Yellow
Write-Host $Messages.Checkpoint0Step1 -ForegroundColor Yellow
Write-Host $Messages.Checkpoint0Step2 -ForegroundColor Yellow
Write-Host $Messages.Checkpoint0Step3 -ForegroundColor Yellow
[void][System.Console]::ReadLine()

# --------------------------------------------------
# Bootstrap: create/update settings_persistent.json and rebuild settings.json
# --------------------------------------------------
$SettingFile             = Join-Path $RootFolder 'Settings\settings.json'
$PersistentDefaultFile   = Join-Path $RootFolder 'Settings\settings_persistent_default.json'

$PythonExe       = Join-Path $InstallationRoot 'Installation\Python311\python.exe'
$BootstrapScript = Join-Path $RootFolder 'Scripts\BootstrapSettings.py'

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python not found: $PythonExe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $BootstrapScript)) {
    Write-Host "[ERROR] Bootstrap script not found: $BootstrapScript" -ForegroundColor Red
    exit 1
}

& $PythonExe $BootstrapScript `
    "$SettingFile" `
    "$DefaultSettingFile" `
    "$PersistentSettingFile" `
    "$PersistentDefaultFile" `
    "$interface_langKey"

if (-not $?) {
    Write-Host "[ERROR] Bootstrap settings failed." -ForegroundColor Red
    exit 1
}


# --------------------------------------------------
# PORTABLE PYTHON PATHS (Direct assignment, no checks)
# --------------------------------------------------
Write-Host ($Messages.Launcher_UsingPortablePython) -ForegroundColor Cyan
# Python 3.11 – Main Project
$Python311Folder = Join-Path $InstallationRoot 'Installation\Python311'
Write-Host ($Messages.Launcher_Python311Path -f $Python311Folder) -ForegroundColor Green
# Python 3.10 – WhisperX Dedicated
$Python310Folder = Join-Path $InstallationRoot 'Installation\Python310'
Write-Host ($Messages.Launcher_Python310Path -f $Python310Folder) -ForegroundColor Green
# Assign to variables for later use in the script
$Python311Exe = Join-Path $Python311Folder 'python.exe'
$Python310Exe = Join-Path $Python310Folder 'python.exe'


# --------------------------------------------------
# Runtime dependency check (ffmpeg, voices_output)
# --------------------------------------------------
$RuntimeDepsScript = Join-Path $ScriptRoot 'RuntimeDependencies.ps1'
if (Test-Path $RuntimeDepsScript) {
    . $RuntimeDepsScript
    $ErrorActionPreference = "Continue"
    Write-Host ""
    $depsOk = Invoke-RuntimeDependencyCheck
    Write-Host ""
    if ($depsOk) {
        Write-Host $Messages.RD_LauncherDepsOk -ForegroundColor Green
    } else {
        Write-Host $Messages.RD_LauncherDepsWarn -ForegroundColor Yellow
    }
} else {
    Write-Host $Messages.RD_LauncherScriptNotFound -ForegroundColor Yellow
}


# --------------------------------------------------
# Workspace structure initialization
# --------------------------------------------------
$savedPythonPath = $env:PYTHONPATH
$env:PYTHONPATH  = $RootFolder
& $Python311Exe -c "from core.workspace_manager import WorkspaceManager; WorkspaceManager.get_active().ensure_structure()"
$env:PYTHONPATH  = $savedPythonPath
if ($?) {
    Write-Host $Messages.Launcher_WorkspaceReady -ForegroundColor Green
} else {
    Write-Host $Messages.Launcher_WorkspaceWarn -ForegroundColor Yellow
}


# ==================================================================
# MAIN FUNCTION - UPDATED
# ==================================================================
function Start-Launcher {
    param([int]$Attempt = 1, [int]$MaxAttempts = 2)

    Write-Host ("== {0} (Attempt {1}) ==" -f $Messages.LauncherStart, $Attempt) -ForegroundColor Blue

    # --------------------------------------------------
    # VENV PATHS
    # --------------------------------------------------
    $VenvPath = Join-Path $RootFolder 'venv'
    $VenvPathWhisper = Join-Path $RootFolder 'venv_whisperX'

    # --------------------------------------------------
    # VENV MANAGEMENT - Main Project
    # --------------------------------------------------
    $VenvManagerPath = Join-Path $RootFolder 'Scripts\VenvManager.ps1'
    $InstallDepsPath = Join-Path $RootFolder 'Scripts\InstallDependencies.ps1'
    $ReqMain = Join-Path $RootFolder 'Scripts\requirements.txt'	
	
    if (Test-Path $VenvManagerPath) {
        Write-Host ($Messages.Launcher_RunningVenvManager -f $VenvManagerPath) -ForegroundColor Cyan
        Write-Host $Messages.Checkpoint1 -ForegroundColor Blue
        $VenvCreated = [bool](& $VenvManagerPath -VenvPath $VenvPath -PythonExe $Python311Exe)				
        if (-not $VenvCreated) { Write-Host $Messages.VenvManagerFailed -ForegroundColor Red; exit 1 }
    } else { 
        Write-Host ($Messages.VenvManagerNotFound -f $VenvManagerPath) -ForegroundColor Red
        exit 1
    }
    # Dependencies installation - Main Project
    if (Test-Path $InstallDepsPath) {
        Write-Host ($Messages.RunningInstallDependencies -f $InstallDepsPath) -ForegroundColor Cyan
        Write-Host $Messages.Checkpoint1_5 -ForegroundColor Blue
        & $InstallDepsPath -VenvPath $VenvPath -RequirementsFile $ReqMain
        if (-not $?) { Write-Host $Messages.InstallDependenciesFailed -ForegroundColor Red; exit 1 }
    } else { 
        Write-Host ($Messages.InstallDependenciesNotFound -f $InstallDepsPath) -ForegroundColor Red
        exit 1
    }


    # --------------------------------------------------
	# VENV MANAGEMENT – WhisperX Project (temporarily disabled)
	# --------------------------------------------------
	# $ReqWhisper = Join-Path $RootFolder 'Scripts\requirementsX.txt'	
	#
	# if (Test-Path $VenvManagerPath) {
	#     Write-Host ($Messages.Launcher_RunningVenvManager -f $VenvManagerPath) -ForegroundColor Cyan
	#     Write-Host $Messages.Checkpoint1 -ForegroundColor Blue
	#     $VenvCreatedWhisper = [bool](& $VenvManagerPath -VenvPath $VenvPathWhisper -PythonExe $Python310Exe)
	#     if (-not $VenvCreatedWhisper) { Write-Host $Messages.VenvManagerFailed -ForegroundColor Red; exit 1 }
	# } else { 
	#     Write-Host ($Messages.VenvManagerNotFound -f $VenvManagerPath) -ForegroundColor Red
	#     exit 1
	# }
	# Dependencies installation – WhisperX
	# if (Test-Path $InstallDepsPath) {
	#     Write-Host ($Messages.RunningInstallDependencies -f $InstallDepsPath) -ForegroundColor Cyan
	#     Write-Host $Messages.Checkpoint1_5 -ForegroundColor Blue
	#     & $InstallDepsPath -VenvPath $VenvPathWhisper -RequirementsFile $ReqWhisper
	#     if (-not $?) { Write-Host $Messages.InstallDependenciesFailed -ForegroundColor Red; exit 1 }
	# } else { 
	#     Write-Host ($Messages.InstallDependenciesNotFound -f $InstallDepsPath) -ForegroundColor Red
	#     exit 1
	# }


	# ==================================================================
	# BLOCCO COMMENTATO: Generate Whisper languages JSON
	# Stiamo commentando questo blocco perché lo script GenerateWhisperLangs.py
	# diventerà uno script di servizio nella cartella maintenance.
	# In futuro, se necessario, possiamo riattivarlo nel Launcher.
	# ==================================================================
    # --------------------------------------------------
	# Generate Whisper languages JSON (only for main venv)
	# --------------------------------------------------
	#$OutputJSON = Join-Path $LocaleFolder 'whisper_languages.json'
	#if (-not (Test-Path $OutputJSON)) {
	#	Write-Host $Messages.GWL_CreatingWhisperLangJSON -ForegroundColor Cyan
	#	$WhisperLangScript = Join-Path $RootFolder 'Scripts\GenerateWhisperLangs.py'
	#	& "$VenvPath\Scripts\python.exe" $WhisperLangScript $OutputJSON
	#	if ($?) { Write-Host $Messages.GWL_WhisperLangJSONCreated -ForegroundColor Green }
	#	else { Write-Host $Messages.GWL_WhisperLangJSONError -ForegroundColor Red }
	#} else {
	#	Write-Host $Messages.GWL_WhisperLangJSONExists -ForegroundColor Yellow
	#}



    # --------------------------------------------------
    # Run Regista.py
    # --------------------------------------------------
    Write-Host $Messages.Checkpoint2 -ForegroundColor Blue
    $registaPath = Join-Path $PSScriptRoot 'Regista.py'
    $env:NUMBA_DISABLE_JIT = "1"

    if (Test-Path $registaPath) {
        Write-Host ($Messages.RegistaFound -f $registaPath) -ForegroundColor Green
        $venvPython = Join-Path $VenvPath 'Scripts\python.exe'
        & $venvPython $registaPath
        if ($?) { Write-Host $Messages.RegistaSuccess -ForegroundColor Green }
        else { Write-Host $Messages.RegistaError -ForegroundColor Red }
    } else { Write-Host ($Messages.RegistaNotFound -f $registaPath) -ForegroundColor Red }

    Write-Host $Messages.LauncherEnd -ForegroundColor Blue
}


# --------------------------------------------------
# Runtime lock: prevent double-start, enable crash recovery
# --------------------------------------------------
$LockFile = Join-Path $RootFolder 'Workspace\runtime.lock'

function Test-LockAlive {
    param([string]$LockPath)
    try {
        $data      = Get-Content $LockPath -Encoding UTF8 -Raw | ConvertFrom-Json
        $proc      = Get-Process -Id ([int]$data.pid) -ErrorAction SilentlyContinue
        $nameNoExt = ($data.process -replace '\.exe$', '')
        return ($null -ne $proc -and $proc.Name -ieq $nameNoExt)
    } catch { return $false }
}

if (Test-Path $LockFile) {
    if (Test-LockAlive $LockFile) {
        Write-Host $Messages.Launcher_AlreadyRunning -ForegroundColor Yellow
        Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
        exit 1
    }
    # Read exit_reason before removing the lock
    $staleLockData = $null
    try { $staleLockData = Get-Content $LockFile -Encoding UTF8 -Raw | ConvertFrom-Json } catch {}
    $wasCleanExit = ($staleLockData -and $staleLockData.clean_exit -eq $true)

    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue

    if (-not $wasCleanExit) {
        # Lock left by a real crash or forced kill — warn the user
        Write-Host $Messages.Launcher_StaleLockRemoved -ForegroundColor Yellow
    }
    # clean_exit (X button, Ctrl+C): silent — no warning needed
}

$currentProc = Get-Process -Id $PID -ErrorAction SilentlyContinue
$procName    = if ($currentProc) { "$($currentProc.Name).exe" } else { "powershell.exe" }
@{ pid = $PID; process = $procName; started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"); hostname = $env:COMPUTERNAME } `
    | ConvertTo-Json | Set-Content -Path $LockFile -Encoding UTF8 -ErrorAction SilentlyContinue

try {
    Start-Launcher
} finally {
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}
