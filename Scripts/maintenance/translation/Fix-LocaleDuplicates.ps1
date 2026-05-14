# ============================================================
# Fix-LocaleDuplicates.ps1
# ============================================================
# Scopo:
#   Rileva e rimuove chiavi duplicate dal file locale sorgente
#   (source_file da config.json), mantenendo sempre l'ultima
#   occorrenza di ogni chiave.
#
# Funzioni principali:
#   - Carica il file JSON in modalità raw per preservare
#     la formattazione originale
#   - Rileva tutte le chiavi duplicate
#   - Modalità DryRun: mostra cosa verrebbe rimosso senza
#     applicare modifiche
#   - Modalità Fix: applica la pulizia e sovrascrive il file,
#     dopo aver creato due backup automatici:
#       * IT_timestamp_pre_dedup.json       → file originale completo
#       * duplicates_removed_timestamp.json → sole righe eliminate
#   - Modalità Safe (default): solo analisi, nessuna modifica
#
# Input (da config.json):
#   source_file   → file JSON da analizzare/correggere
#   report_folder → cartella dove salvare i backup
#
# Utilizzo:
#   .\Fix-LocaleDuplicates.ps1              → analisi only (safe)
#   .\Fix-LocaleDuplicates.ps1 -DryRun      → simula la pulizia
#   .\Fix-LocaleDuplicates.ps1 -Fix         → applica la pulizia
#
# Consigliato come primo step prima di LocaleKeyAnalyzer.ps1.
# ============================================================

param(
    [switch]$Fix,
    [switch]$DryRun
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

# ============================================================
# 1. PROJECT ROOT DETECTION
# ============================================================

function Get-ProjectRoot {
    $dir = $PSScriptRoot
    while ($dir) {
        if (Test-Path (Join-Path $dir "Locale")) { return $dir }
        $parent = Split-Path $dir -Parent
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    return $null
}

$projectRoot = Get-ProjectRoot

if (-not $projectRoot) {
    Write-Host "[ERROR] Project root not found"
    exit 1
}

# ============================================================
# 2. LOAD CONFIG
# ============================================================

$configPath = Join-Path $PSScriptRoot "config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "[ERROR] config.json not found at: $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# ============================================================
# 3. RESOLVE PATHS FROM CONFIG
# ============================================================

$sourcePath     = Join-Path $projectRoot $config.source_file
$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)
$reportDir      = Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName
$backupDir      = Join-Path (Join-Path $projectRoot $config.backup_folder) $sourceBaseName

if (-not (Test-Path $sourcePath)) {
    Write-Host "[ERROR] source_file not found: $sourcePath"
    exit 1
}

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

# ============================================================
# 4. LOG HEADER
# ============================================================

Write-Host "`n==============================="
Write-Host " LOCALE DUPLICATE ANALYZER"
Write-Host "==============================="
Write-Host ""
Write-Host "[INPUT]"
Write-Host "Source : $sourcePath"
Write-Host ""

if (-not $Fix -and -not $DryRun) {
    Write-Host "[SAFE MODE] Solo analisi. Nessuna modifica verra' applicata.`n"
}

# ============================================================
# 5. LOAD + PARSE RAW JSON
# ============================================================

$raw = [System.IO.File]::ReadAllText($sourcePath, [System.Text.Encoding]::UTF8)

$rawMatches = [regex]::Matches(
    $raw,
    '"(?<key>[^"]+)"\s*:\s*(?<value>.+?)(,?)(\r?\n|$)',
    'Singleline'
)

# ============================================================
# 6. FILE METRICS
# ============================================================

$rawLines = $raw -split "`r?`n"

if ($rawLines -and $rawLines.Count -gt 0) {
    if (($rawLines[-1] -as [string]).Trim() -eq "") {
        $rawLines = $rawLines[0..($rawLines.Count - 2)]
    }
}

$blankLines = ($rawLines | Where-Object { ($_ -as [string]).Trim() -eq "" }).Count
$totalLines = $rawLines.Count

# ============================================================
# 7. BUILD ENTRY LIST
# ============================================================

$entries = @()

foreach ($m in $rawMatches) {
    $entries += [PSCustomObject]@{
        RawLine = $m.Value
        Key     = $m.Groups["key"].Value
    }
}

$uniqueKeyCount = ($entries | Select-Object -ExpandProperty Key | Sort-Object -Unique).Count

Write-Host "[PARSE RESULT]"
Write-Host "Entries loaded : $($entries.Count)"
Write-Host "Unique keys    : $uniqueKeyCount"

# ============================================================
# 8. DETECT DUPLICATES
# ============================================================

$groups     = $entries | Group-Object Key
$duplicates = $groups  | Where-Object { $_.Count -gt 1 }

Write-Host ""

if ($duplicates) {
    Write-Host "[WARNING] Duplicate keys found:"
    foreach ($g in $duplicates) {
        Write-Host "  - $($g.Name) (x$($g.Count))"
    }
} else {
    Write-Host "[OK] Nessuna chiave duplicata trovata"
}

# ============================================================
# 9. LAST OCCURRENCE MAP
# ============================================================

$lastOccurrence = @{}

for ($i = 0; $i -lt $entries.Count; $i++) {
    $lastOccurrence[$entries[$i].Key] = $i
}

# ============================================================
# 10. DRY RUN
# ============================================================

if ($DryRun) {

    Write-Host "`n[DRY RUN] Nessuna modifica applicata"

    $removedMap = @{}

    for ($i = 0; $i -lt $entries.Count; $i++) {
        $key = $entries[$i].Key
        if ($lastOccurrence[$key] -ne $i) {
            if (-not $removedMap.ContainsKey($key)) { $removedMap[$key] = 0 }
            $removedMap[$key]++
        }
    }

    $removedTotal = ($removedMap.Values | Measure-Object -Sum).Sum

    Write-Host "`n[DRY RUN RESULT]"
    Write-Host "Input entries  : $($entries.Count)"
    Write-Host "Removed keys   : $($removedMap.Count)"
    Write-Host "Removed items  : $removedTotal"
    Write-Host "Output entries : $($entries.Count - $removedTotal)"

    if ($removedMap.Count -gt 0) {
        Write-Host "`n[REMOVE SUMMARY]"
        foreach ($k in $removedMap.Keys) {
            Write-Host "  [REMOVE] $k (x$($removedMap[$k]))"
        }
    }

    Write-Host "`n[INFO] Simulazione completata"
    exit 0
}

# ============================================================
# 11. FIX — BACKUP ORIGINALE + CHIAVI RIMOSSE
# ============================================================

if ($Fix) {

    $timestamp      = Get-Date -Format "yyyyMMdd"
    $sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($sourcePath)
    $sourceExt      = [System.IO.Path]::GetExtension($sourcePath)
    $sourceDir      = [System.IO.Path]::GetDirectoryName($sourcePath)

    # calcola numero progressivo per pre_dedup
    $counter = 1
    while (Test-Path (Join-Path $backupDir "${sourceBaseName}_pre_dedup_${counter}_${timestamp}${sourceExt}")) {
        $counter++
    }

    # backup file originale completo
    $backupPath = Join-Path $backupDir "${sourceBaseName}_pre_dedup_${counter}_${timestamp}${sourceExt}"
    Copy-Item $sourcePath $backupPath

    Write-Host "`n[BACKUP CREATED]"
    Write-Host "  Original : $backupPath"

    # raccogli le righe duplicate da rimuovere per il backup
    $removedLines = @()

    for ($i = 0; $i -lt $entries.Count; $i++) {
        $key = $entries[$i].Key
        if ($lastOccurrence[$key] -ne $i) {
            $removedLines += $entries[$i].RawLine.TrimEnd()
        }
    }

    # salva le chiavi rimosse in backup_folder
    $removedBackupPath = Join-Path $backupDir "${sourceBaseName}_duplicates_removed_${counter}_${timestamp}.json"
    $removedLines | Set-Content $removedBackupPath -Encoding UTF8

    Write-Host "  Removed  : $removedBackupPath"
}

# ============================================================
# 12. FIX — WRITE CLEAN FILE (sovrascrive il sorgente)
# ============================================================

if ($Fix) {

    $outputLines = @()
    $seen        = @{}

    $outputLines += "{"

    for ($i = 0; $i -lt $entries.Count; $i++) {

        $key = $entries[$i].Key

        if ($lastOccurrence[$key] -ne $i) { continue }
        if ($seen.ContainsKey($key))       { continue }

        $seen[$key] = $true
        $outputLines += ($entries[$i].RawLine.TrimEnd())
    }

    $outputLines += "}"

    $outputLines | Set-Content $sourcePath -Encoding UTF8

    $script:finalCount = $outputLines.Count - 2
}

# ============================================================
# 13. FINAL REPORT
# ============================================================

$inputCount   = $entries.Count
$outputCount  = if ($Fix) { $script:finalCount } else { $entries.Count }
$removedCount = if ($Fix) { $inputCount - $outputCount } else { 0 }

Write-Host "`n[PROCESS RESULT]"
Write-Host "Input entries  : $inputCount"
Write-Host "Output entries : $outputCount"
Write-Host "Removed        : $removedCount"

Write-Host "`n[STRUCTURE METRICS]"
Write-Host "Total file lines : $totalLines"
Write-Host "Blank lines      : $blankLines"
Write-Host "Non-blank lines  : $($totalLines - $blankLines)"

Write-Host "`n[LOGICAL METRICS]"
Write-Host "Total key occurrences : $($entries.Count)"
Write-Host "Unique keys           : $uniqueKeyCount"

Write-Host "`n[MODE SUMMARY]"

if ($Fix) {
    Write-Host "Mode   : FIX"
    Write-Host "Action : Source overwritten, backups created in backup folder"
} elseif ($DryRun) {
    Write-Host "Mode   : DRY RUN"
    Write-Host "Action : No changes applied"
} else {
    Write-Host "Mode   : SAFE"
    Write-Host "Action : Analysis only"
}
