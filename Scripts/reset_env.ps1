# =========================================================
# Scripts/reset_env.ps1
# =========================================================
# Description:
#   Hard reset triggered by settings_manager.hard_reset().
#   Runs when reset.json has reset_pending = true.
#
#   Steps:
#     1. Restore settings_persistent.json from settings_persistent_default.json
#     2. Rebuild settings.json via BootstrapSettings.py (merge)
#     3. Delete venv/ to force full environment rebuild on next launch
#     4. Clear reset_pending flag in reset.json
#
# Language rule:
#   All comments must be written in English.
# =========================================================

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir

$SettingsFolder         = Join-Path $ProjectRoot "Settings"
$ResetFile              = Join-Path $SettingsFolder "reset.json"
$SettingsFile           = Join-Path $SettingsFolder "settings.json"
$DefaultSettingsFile    = Join-Path $SettingsFolder "settings_default.json"
$PersistentFile         = Join-Path $SettingsFolder "settings_persistent.json"
$PersistentDefaultFile  = Join-Path $SettingsFolder "settings_persistent_default.json"
$VenvFolder             = Join-Path $ProjectRoot "venv"
$PythonExe              = Join-Path $ProjectRoot "Installation\Python311\python.exe"
$BootstrapScript        = Join-Path $ScriptDir "BootstrapSettings.py"

$LocaleFile = Join-Path $ProjectRoot "locale\Active\it.json"
$Messages   = Get-Content $LocaleFile -Raw -Encoding UTF8 | ConvertFrom-Json

try {
    $ResetData = Get-Content $ResetFile -Raw | ConvertFrom-Json

    if ($ResetData.reset_pending -ne $true) {
        Write-Host $Messages.Reset_No_Reset_Pending -ForegroundColor Yellow
        exit 0
    }

    Write-Host $Messages.Reset_Requested -ForegroundColor Yellow

    # 1. Restore settings_persistent.json from defaults
    Copy-Item -Path $PersistentDefaultFile -Destination $PersistentFile -Force
    Write-Host "[OK] settings_persistent.json restored from defaults." -ForegroundColor Green

    # 2. Rebuild settings.json via BootstrapSettings.py
    & $PythonExe $BootstrapScript `
        "$SettingsFile" `
        "$DefaultSettingsFile" `
        "$PersistentFile" `
        "$PersistentDefaultFile"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] BootstrapSettings.py failed during hard reset." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] settings.json rebuilt from defaults." -ForegroundColor Green

    # 3. Delete venv/ — rename first for safety, then delete
    if (Test-Path $VenvFolder) {
        $VenvOld = "$VenvFolder`_old"
        if (Test-Path $VenvOld) {
            Remove-Item -Recurse -Force $VenvOld
        }
        Rename-Item -Path $VenvFolder -NewName "$($VenvFolder)_old"
        Remove-Item -Recurse -Force $VenvOld
        Write-Host "[OK] Virtual environment deleted. It will be rebuilt on next launch." -ForegroundColor Green
    }

    # 4. Clear reset flag
    $ResetData.reset_pending = $false
    $ResetData.first_launch  = $true
    $ResetData | ConvertTo-Json | Set-Content $ResetFile -Encoding UTF8

    Write-Host $Messages.Reset_Completed -ForegroundColor Green

} catch {
    Write-Host $Messages.Reset_Error -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    exit 1
}
