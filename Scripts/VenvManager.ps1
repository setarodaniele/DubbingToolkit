# ==================================================================
# VenvManager.ps1 - Clean Refactored Version (FINAL)
# ==================================================================

param(
    [string]$VenvPath = "$(Split-Path $PSScriptRoot -Parent)\venv",
    [string]$PythonExe = "$(Split-Path $PSScriptRoot -Parent)\Installation\Python311\python.exe"
)

# ==================================================================
# FORCE UTF-8 ENCODING
# ==================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    if ($PSVersionTable.PSEdition -eq "Desktop") {
        chcp 65001 | Out-Null
    }
} catch { }

# ==================================================================
# PATH CONFIGURATION
# ==================================================================
$RootFolder = Split-Path $PSScriptRoot -Parent
$VenvPath   = Join-Path $RootFolder "venv"
$PythonExe  = Join-Path $RootFolder "Installation\Python311\python.exe"

# ==================================================================
# MODULES IMPORT
# ==================================================================
Import-Module "$RootFolder\ps\Messages.psm1" -Force
Import-Module "$RootFolder\ps\Logging.psm1" -Force

# ==================================================================
# SETTINGS + MESSAGES INIT
# ==================================================================
$SettingsFile = Join-Path $RootFolder 'Settings\settings.json'
$Settings      = Get-Content $SettingsFile -Encoding UTF8 | ConvertFrom-Json

$interface_langKey = $Settings.interface_lang

$messagesFile = Join-Path $RootFolder "Locale\Active\$interface_langKey.json"
Set-Messages (Get-Content $messagesFile -Encoding UTF8 | ConvertFrom-Json)

# ==================================================================
# START
# ==================================================================
Write-Log "VenvManagerStart" "INFO"

# ==================================================================
# 1) TEST VENV STRUCTURE
# ==================================================================
function Test-VenvStructure {
    param([string]$Path)

    if (-not (Test-Path $Path)) { return "Missing" }

    try {
        $contents = Get-ChildItem -LiteralPath $Path -Force -ErrorAction Stop
        if ($contents.Count -eq 0) { return "Invalid" }
    } catch {
        return "Invalid"
    }

    $RequiredPaths = @(
        "Scripts\python.exe",
        "Scripts\pip.exe",
        "Lib\site-packages",
        "Include",
        "pyvenv.cfg"
    )

    foreach ($rel in $RequiredPaths) {
        if (-not (Test-Path (Join-Path $Path $rel))) {
            return "Invalid"
        }
    }

    return "Valid"
}

# ==================================================================
# 2) TEST PYENV.CFG
# ==================================================================
function Test-PyEnvCfg {
    param([string]$Path)

    $cfgPath = Join-Path $Path "pyvenv.cfg"
    if (-not (Test-Path $cfgPath)) { return "Missing" }

    $cfgContent = Get-Content $cfgPath -ErrorAction SilentlyContinue
    $homeLine = $cfgContent | Where-Object { $_ -match "^home\s*=" }

    if (-not $homeLine) { return "Mismatch" }

    $cfgHomePath = ($homeLine -split "=")[1].Trim()

    try {
        $cfgNormalized = (Resolve-Path $cfgHomePath).Path.TrimEnd('\')
        $expectedNormalized = (Split-Path (Resolve-Path $PythonExe).Path -Parent).TrimEnd('\')
    } catch {
        return "Mismatch"
    }

    if ($cfgNormalized -ne $expectedNormalized) {
        return "Mismatch"
    }

    return "Valid"
}

# ==================================================================
# 3) TEST PYTHON RUNTIME
# ==================================================================
function Test-VenvRuntime {
    param([string]$Path)

    $python = Join-Path $Path "Scripts\python.exe"

    if (-not (Test-Path $python)) { return "Failed" }

    try {
        & $python -c "import sys" | Out-Null
        return "Valid"
    } catch {
        return "Failed"
    }
}

# ==================================================================
# 4) TEST PIP MODULE
# ==================================================================
function Test-PipModule {
    param([string]$Path)

    $python = Join-Path $Path "Scripts\python.exe"

    if (-not (Test-Path $python)) { return "Failed" }

    try {
        & $python -m pip --version | Out-Null
        return "Valid"
    } catch {
        return "Failed"
    }
}

# ==================================================================
# 5) TEST PIP EXE (LAUNCHER)
# ==================================================================
function Test-PipExe {
    param([string]$Path)

    $pip = Join-Path $Path "Scripts\pip.exe"

    if (-not (Test-Path $pip)) {
        return "Missing"
    }

    try {
        & $pip --version | Out-Null
        return "Valid"
    } catch {
        return "Failed"
    }
}

# ==================================================================
# 6) REMOVE VENV
# ==================================================================
function Remove-VenvFolder {
    param([string]$Path)

    try {
        Remove-Item $Path -Recurse -Force -ErrorAction Stop
        Write-Log "VenvCleanup" "INFO" @($Path)
        return $true
    } catch {
        Write-Log "VenvCleanupFail" "ERROR" @($Path)
        return $false
    }
}

# ==================================================================
# 7) CREATE VENV
# ==================================================================
function Create-VenvFolder {
    param([string]$Path)

    Write-Log "VenvCreatingPath" "INFO" @($Path)

    try {
        & $PythonExe -m venv $Path
    } catch {
        return "Failed"
    }

    $Activate = Join-Path $Path 'Scripts\Activate.ps1'

    if (Test-Path $Activate) {
        Write-Log "VenvCreated" "INFO" @($Path)
        return "Created"
    }

    Write-Log "VenvCreateError" "ERROR"
    return "Failed"
}

# ==================================================================
# 8) FULL REPAIR
# ==================================================================
$EnableSafetyPrompt = $false

function Repair-VenvFull {
    param([string]$Path)

    if (Test-Path $Path) {

        if ($EnableSafetyPrompt) {
            $confirm = Read-Host (Get-Message "VenvConfirmDeletePrompt")

            if ($confirm -ne "YES") {
                Write-Log "VenvDeleteAborted" "WARN"
                return $false
            }
        }

        Write-Log "VenvRemoving" "INFO"
        Remove-VenvFolder -Path $Path | Out-Null
    }

    Write-Log "VenvRecreating" "INFO" @($Path)

    $result = Create-VenvFolder -Path $Path

    if ($result -ne "Created") {
        Write-Log "VenvCreateFail" "ERROR"
        return $false
    }

    return $true
}

# ==================================================================
# 9) ORCHESTRATOR
# ==================================================================
function Regista-Venv {
    param([string]$Path)

    Write-Log "VenvValidationStart" "INFO"

    $lvl1 = Test-VenvStructure -Path $Path
    if ($lvl1 -ne "Valid") {
        Write-Log "VenvStructureInvalid" "ERROR"
        return Repair-VenvFull -Path $Path
    }

    $lvl2 = Test-PyEnvCfg -Path $Path
    if ($lvl2 -ne "Valid") {
        Write-Log "VenvCfgMismatch" "ERROR"
        return Repair-VenvFull -Path $Path
    }

    $lvl3 = Test-VenvRuntime -Path $Path
    if ($lvl3 -ne "Valid") {
        Write-Log "VenvPythonRuntimeInvalid" "ERROR"
        return Repair-VenvFull -Path $Path
    }

    $lvl4 = Test-PipModule -Path $Path
    if ($lvl4 -ne "Valid") {
        Write-Log "VenvPipModuleMissing" "ERROR"
        return Repair-VenvFull -Path $Path
    }

    $lvl5 = Test-PipExe -Path $Path
    if ($lvl5 -ne "Valid") {
        Write-Log "VenvPipLauncherBroken" "ERROR"
        return Repair-VenvFull -Path $Path
    }

    Write-Log "VenvValidationSuccess" "INFO" @($Path)
    return $true
}

# ==================================================================
# EXECUTION
# ==================================================================
$VenvCreated = Regista-Venv -Path $VenvPath

if (-not $VenvCreated) {
    Write-Log "VenvCreateFail" "ERROR"
    exit 1
}

# ==================================================================
# ACTIVATE VENV
# ==================================================================
$ActivateScript = Join-Path $VenvPath 'Scripts\Activate.ps1'

if (Test-Path $ActivateScript) {
    Write-Log "VenvActivating" "INFO" @($VenvPath)

    try {
        . $ActivateScript
        Write-Log "VenvActivated" "INFO" @($VenvPath)
    } catch {
        Write-Log "VenvActivateError" "ERROR"
        exit 1
    }
}

Write-Log "VenvManagerEnd" "INFO"

return $VenvCreated