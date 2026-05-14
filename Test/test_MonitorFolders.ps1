# ==================================================================
# MonitorFolders.ps1 - Monitor folder sizes for Dubbing Toolkit
# ==================================================================

param(
    [string]$RootFolder = "$(Split-Path $PSScriptRoot -Parent)",
    [int]$IntervalSec = 2,
    [int]$TimeoutSec = 300  # default 5 minuti
)

# Load localization messages (ITjson)
$MessagesFile = Join-Path $RootFolder "Locale\Active\it.json"
$Messages = Get-Content $MessagesFile -Encoding UTF8 | ConvertFrom-Json

# Define relative folders to monitor
$RelativeFolders = @(
    "venv",
    "venv_whisperX",
    "Audio_Extracted"
)

# Resolve absolute paths
$FoldersToMonitor = $RelativeFolders | ForEach-Object { Join-Path $RootFolder $_ }

# Initialize previous sizes and line mapping
$PrevSizes = @{}
$FolderLines = @{}
$Row = 0

Clear-Host
foreach ($folder in $FoldersToMonitor) {
    if (Test-Path $folder) {
        $PrevSizes[$folder] = 0
        Write-Host ("{0,-40} {1,10:N2} MB" -f (Split-Path $folder -Leaf), 0) -ForegroundColor White
        $FolderLines[$folder] = $Row
        $Row++
    }
}

$StartTime = Get-Date

# ==================================================================
# Monitoring loop
# ==================================================================
while ($true) {

    foreach ($folder in $FoldersToMonitor) {
        if (-not (Test-Path $folder)) { continue }

        $size = (Get-ChildItem $folder -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)

        $host.UI.RawUI.CursorPosition = @{X=0;Y=$FolderLines[$folder]}

        if ($sizeMB -ne $PrevSizes[$folder]) {
            Write-Host ("{0,-40} {1,10:N2} MB" -f (Split-Path $folder -Leaf), $sizeMB) -ForegroundColor Yellow
            $PrevSizes[$folder] = $sizeMB
        } else {
            Write-Host ("{0,-40} {1,10:N2} MB" -f (Split-Path $folder -Leaf), $sizeMB) -ForegroundColor White
        }
    }

    Start-Sleep -Seconds $IntervalSec

    # Check timeout
    if ((Get-Date) - $StartTime -gt (New-TimeSpan -Seconds $TimeoutSec)) {
        Write-Host ($Messages.MonitorTimeout) -ForegroundColor Cyan
        break
    }
}

Write-Host ($Messages.MonitorEnd) -ForegroundColor Cyan
