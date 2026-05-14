# =========================================================
# Scripts/RuntimeDependencies.ps1
# =========================================================
# Description:
#   Ensures required runtime dependencies (ffmpeg, voices_output) are present.
#   Checks local paths first; downloads and extracts from GitHub if missing.
#   Designed to run once at install time and skip silently on subsequent runs.
#
# Inputs:
#   - None (all paths are derived from script location)
#
# Outputs:
#   - $true  : all required dependencies are present (or successfully installed)
#   - $false : one or more required dependencies could not be resolved
#   - Logs\runtime_dependencies.log (appended on every run)
#
# Notes:
#   - Uses Tools/7zr.exe (7-Zip standalone CLI) for .7z extraction
#   - ffmpeg: downloads ffmpeg-7.1.1-full_build.7z from GyanD/codexffmpeg on GitHub
#   - voices: downloads voices_output archive from GitHub Releases (URL must be configured)
#   - Safe to call on every launch - skips download if expected files already exist
#   - Can be dot-sourced from Launcher.ps1 or run standalone for testing
#   - When dot-sourced, uses $Messages already loaded by Launcher
#   - When standalone, loads $Messages from settings.json + locale/Active/<lang>.json
#
# Language rule:
#   All comments must be written in English.
# =========================================================


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


# =========================================================
# 1. IMPORTS / DEPENDENCIES
# =========================================================
# 1.1 No external module dependencies - stdlib and .NET only


# =========================================================
# 2. CONFIGURATION
# =========================================================
# 2.1 Root paths

$RD_ScriptDir  = $PSScriptRoot
$RD_RootFolder = Split-Path $RD_ScriptDir -Parent

# 2.2 ffmpeg paths

$RD_FfmpegVersion     = "7.1.1"
$RD_FfmpegDirName     = "ffmpeg-$RD_FfmpegVersion-full_build"
$RD_FfmpegDir         = Join-Path $RD_RootFolder "Tools\$RD_FfmpegDirName"
$RD_FfmpegExe         = Join-Path $RD_FfmpegDir  "bin\ffmpeg.exe"
$RD_ToolsDir          = Join-Path $RD_RootFolder "Tools"

# 2.3 Voices paths

$RD_VoicesDir         = Join-Path $RD_RootFolder "voices"
$RD_VoicesOutputDir   = Join-Path $RD_VoicesDir  "voices_output"

# 2.4 Log paths

$RD_LogDir  = Join-Path $RD_RootFolder "Logs"
$RD_LogFile = Join-Path $RD_LogDir "runtime_dependencies.log"

# 2.5 Download URLs

$RD_FfmpegArchiveName  = "ffmpeg-$RD_FfmpegVersion-full_build.7z"
$RD_FfmpegUrl          = "https://github.com/GyanD/codexffmpeg/releases/download/$RD_FfmpegVersion/$RD_FfmpegArchiveName"

$RD_VoicesArchiveName  = "voices_output.7z"
$RD_VoicesUrl          = "https://github.com/SmallSoftwareHouse/DubbingToolkit/releases/download/v0.1.0-alpha/voices_output.7z"

# 2.6 7-Zip standalone CLI (bundled in Tools/)

$RD_7zrExe = Join-Path $RD_ToolsDir '7zr.exe'


# =========================================================
# 3. UTILITIES
# =========================================================
# 3.1 Initialize-RDMessages - load $Messages if not already available (standalone mode)
# 3.2 Get-RDMsg             - look up a locale key from $Messages with fallback
# 3.3 Write-RDLog           - write timestamped entry to console and log file
# 3.4 Get-HumanSize         - format a byte count as a human-readable string

function Initialize-RDMessages {
    if (Get-Variable -Name 'Messages' -ErrorAction SilentlyContinue) { return }

    $lang = "en"
    try {
        $settingsPath = Join-Path $RD_RootFolder "Settings\settings.json"
        if (Test-Path $settingsPath) {
            $s = Get-Content $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($s.interface_lang) { $lang = $s.interface_lang }
        }
        $localeFile = Join-Path $RD_RootFolder "locale\Active\$lang.json"
        if (-not (Test-Path $localeFile)) {
            $localeFile = Join-Path $RD_RootFolder "locale\Active\en.json"
        }
        $global:Messages = Get-Content $localeFile -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $global:Messages = [PSCustomObject]@{}
    }
}

function Get-RDMsg {
    param([string]$Key, [object[]]$Params = @())
    $msgObj = Get-Variable -Name 'Messages' -ErrorAction SilentlyContinue
    $val = if ($msgObj -and $msgObj.Value -and $msgObj.Value.PSObject.Properties[$Key]) {
        $msgObj.Value.$Key
    } else {
        "[RD:$Key]"
    }
    if ($Params.Count -gt 0) { return ($val -f $Params) }
    return $val
}

function Write-RDLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "OK")][string]$Level = "INFO"
    )
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$timestamp] [$Level] $Message"

    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        "OK"    { "Green" }
    }
    Write-Host $line -ForegroundColor $color

    try {
        if (-not (Test-Path $RD_LogDir)) {
            New-Item -ItemType Directory -Path $RD_LogDir -Force | Out-Null
        }
        Add-Content -Path $RD_LogFile -Value $line -Encoding UTF8
    } catch {
        # Log write failure is non-fatal
    }
}

function Get-HumanSize {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:F1} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:F1} MB" -f ($Bytes / 1MB) }
    return "{0:F0} KB" -f ($Bytes / 1KB)
}

# Load locale messages (no-op if already loaded by Launcher)
Initialize-RDMessages


# =========================================================
# 4. CORE LOGIC
# =========================================================
# 4.1 Test-FfmpegPresent   - check if ffmpeg.exe exists at the expected path
# 4.2 Test-VoicesPresent   - check if voices_output contains at least one provider subdir
# 4.3 Invoke-RDDownload    - download a file from URL using WebClient (streams to disk)
# 4.4 Invoke-FfmpegSetup   - download, extract, and verify ffmpeg
# 4.5 Invoke-VoicesSetup   - download, extract, and verify voices_output

function Test-FfmpegPresent {
    return (Test-Path $RD_FfmpegExe)
}

function Test-VoicesPresent {
    if (-not (Test-Path $RD_VoicesOutputDir)) { return $false }
    $subdirs = Get-ChildItem -Path $RD_VoicesOutputDir -Directory -ErrorAction SilentlyContinue |
               Where-Object { $_.Name -ne "nppBackup" }
    return ($null -ne $subdirs -and $subdirs.Count -gt 0)
}

function Invoke-RDDownload {
    param(
        [string]$Url,
        [string]$Destination
    )
    Write-RDLog (Get-RDMsg "RD_Downloading" $Url)
    Write-RDLog (Get-RDMsg "RD_SavingTo" $Destination)
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    $wc = $null
    try {
        $wc = [System.Net.WebClient]::new()
        $wc.Headers.Add("User-Agent", "DubbingToolkit-RuntimeSetup")
        $wc.DownloadFile($Url, $Destination)
        $size = (Get-Item $Destination).Length
        Write-RDLog (Get-RDMsg "RD_DownloadComplete" (Get-HumanSize $size)) "OK"
        return $true
    } catch {
        Write-RDLog (Get-RDMsg "RD_DownloadFailed" $_) "ERROR"
        return $false
    } finally {
        if ($null -ne $wc) { $wc.Dispose() }
    }
}

function Invoke-FfmpegSetup {
    Write-RDLog (Get-RDMsg "RD_FfmpegDownloading")
    $tempArchive = Join-Path $RD_ToolsDir $RD_FfmpegArchiveName

    if (-not (Test-Path $RD_ToolsDir)) {
        New-Item -ItemType Directory -Path $RD_ToolsDir -Force | Out-Null
    }

    $downloaded = Invoke-RDDownload -Url $RD_FfmpegUrl -Destination $tempArchive
    if (-not $downloaded) { return $false }

    Write-RDLog (Get-RDMsg "RD_Extracting" $RD_FfmpegArchiveName)
    try {
        & $RD_7zrExe x $tempArchive "-o$RD_ToolsDir"
        if ($LASTEXITCODE -ne 0) { throw "7zr exited with code $LASTEXITCODE" }
        Write-RDLog (Get-RDMsg "RD_ExtractionComplete") "OK"
    } catch {
        Write-RDLog (Get-RDMsg "RD_ExtractionFailed" $_) "ERROR"
        Remove-Item $tempArchive -Force -ErrorAction SilentlyContinue
        return $false
    } finally {
        if (Test-Path $tempArchive) {
            Remove-Item $tempArchive -Force -ErrorAction SilentlyContinue
            Write-RDLog (Get-RDMsg "RD_ArchiveRemoved")
        }
    }

    if (Test-FfmpegPresent) {
        Write-RDLog (Get-RDMsg "RD_FfmpegVerified" $RD_FfmpegExe) "OK"
        return $true
    } else {
        Write-RDLog (Get-RDMsg "RD_FfmpegNotFoundAfterExtract") "ERROR"
        return $false
    }
}

function Invoke-VoicesSetup {
    if ([string]::IsNullOrWhiteSpace($RD_VoicesUrl)) {
        Write-RDLog (Get-RDMsg "RD_VoicesUrlMissing") "WARN"
        return $false
    }

    Write-RDLog (Get-RDMsg "RD_VoicesDownloading")
    $tempArchive = Join-Path $RD_VoicesDir $RD_VoicesArchiveName

    if (-not (Test-Path $RD_VoicesDir)) {
        New-Item -ItemType Directory -Path $RD_VoicesDir -Force | Out-Null
    }

    $downloaded = Invoke-RDDownload -Url $RD_VoicesUrl -Destination $tempArchive
    if (-not $downloaded) { return $false }

    Write-RDLog (Get-RDMsg "RD_Extracting" $RD_VoicesArchiveName)
    try {
        & $RD_7zrExe x $tempArchive "-o$RD_VoicesDir"
        if ($LASTEXITCODE -ne 0) { throw "7zr exited with code $LASTEXITCODE" }
        Write-RDLog (Get-RDMsg "RD_ExtractionComplete") "OK"
    } catch {
        Write-RDLog (Get-RDMsg "RD_ExtractionFailed" $_) "ERROR"
        Remove-Item $tempArchive -Force -ErrorAction SilentlyContinue
        return $false
    } finally {
        if (Test-Path $tempArchive) {
            Remove-Item $tempArchive -Force -ErrorAction SilentlyContinue
            Write-RDLog (Get-RDMsg "RD_ArchiveRemoved")
        }
    }

    if (Test-VoicesPresent) {
        Write-RDLog (Get-RDMsg "RD_VoicesVerified" $RD_VoicesOutputDir) "OK"
        return $true
    } else {
        Write-RDLog (Get-RDMsg "RD_VoicesMissingAfterExtract") "ERROR"
        return $false
    }
}


# =========================================================
# 5. MAIN EXECUTION
# =========================================================
# 5.1 Invoke-RuntimeDependencyCheck - public entry point, call from Launcher.ps1
# 5.2 Returns $true if all required dependencies are present or installed
# 5.3 voices_output failure is non-fatal (WARN only) - app can run without voice samples

function Invoke-RuntimeDependencyCheck {
    Write-RDLog (Get-RDMsg "RD_CheckStart")
    $allOk = $true

    # --- ffmpeg ---
    if (Test-FfmpegPresent) {
        Write-RDLog (Get-RDMsg "RD_FfmpegPresent") "OK"
    } else {
        $ok = Invoke-FfmpegSetup
        if (-not $ok) {
            Write-RDLog (Get-RDMsg "RD_FfmpegSetupFailed") "ERROR"
            $allOk = $false
        }
    }

    # --- voices_output ---
    if (Test-VoicesPresent) {
        Write-RDLog (Get-RDMsg "RD_VoicesPresent") "OK"
    } else {
        $ok = Invoke-VoicesSetup
        if (-not $ok) {
            # Non-fatal: voices are used for TTS preview only
            Write-RDLog (Get-RDMsg "RD_VoicesNotAvailable") "WARN"
        }
    }

    $status = if ($allOk) { "OK" } else { "PARTIAL" }
    Write-RDLog (Get-RDMsg "RD_CheckEnd" $status) $(if ($allOk) { "OK" } else { "WARN" })
    return $allOk
}

# Run standalone if executed directly (not dot-sourced)
if ($MyInvocation.InvocationName -ne '.') {
    Invoke-RuntimeDependencyCheck
}
