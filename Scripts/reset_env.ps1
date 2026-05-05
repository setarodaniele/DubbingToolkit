# ========================================================
# reset_env.ps1 – Hard Reset Safe Test Version
# ========================================================

# Root folder (cartella Scripts)
$RootFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Project root (parent di Scripts)
$ProjectRoot = Split-Path -Parent $RootFolder

# Paths principali
$SettingsFolder       = Join-Path $ProjectRoot "Settings"
$ResetFile            = Join-Path $SettingsFolder "reset.json"
$SettingsFile         = Join-Path $SettingsFolder "settings.json"
$DefaultSettingsFile  = Join-Path $SettingsFolder "settings_default.json"
$Launcher             = Join-Path $ProjectRoot "launcher.ps1"
$VenvFolder           = Join-Path $ProjectRoot "venv"

# Load messages
$LocaleFile = Join-Path $ProjectRoot "Locale\Active\it.json"
$Messages   = Get-Content $LocaleFile | ConvertFrom-Json




# ========================================================
# Hard reset – safe test block
# ========================================================
try {
    # Read reset.json
    $ResetData = Get-Content $ResetFile | ConvertFrom-Json

    if ($ResetData.reset_pending -eq $true) {
        Write-Host $Messages.Reset_Requested

        # Overwrite settings.json with defaults
        Copy-Item -Path $DefaultSettingsFile -Destination $SettingsFile -Force

        # Update reset flags
        $ResetData.reset_pending = $false
        $ResetData.first_launch = $true
        $ResetData | ConvertTo-Json | Set-Content $ResetFile


        # ========================================================
        # STOP prima di eliminare il venv
        # ========================================================
        Write-Host ">>> SAFE TEST MODE: STOP BEFORE VENV DELETION <<<"
        Write-Host "Virtual environment would be here: $VenvFolder"
        Write-Host "Press Ctrl+C to stop, or comment this exit line to continue with real deletion."
        Write-Host $Messages.Reset_Completed
		
        exit 0

        # ========================================================
        # Venv deletion (real hard reset)
        # ========================================================
        # if (Test-Path $VenvFolder) {
        #     Write-Host "Deleting virtual environment..."
        #     Remove-Item -Recurse -Force $VenvFolder
        # }

        # Relaunch launcher
        # Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$Launcher`"" -Wait
		
		
    } else {
        Write-Host $Messages.Reset_No_Reset_Pending
    }
}
catch {
    Write-Host $Messages.Reset_Error
}
