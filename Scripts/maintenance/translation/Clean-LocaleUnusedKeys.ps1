# ============================================================
# Clean-LocaleUnusedKeys.ps1
# ============================================================
# Scopo:
#   Rimuove dal file locale sorgente (source_file da config.json)
#   tutte le chiavi identificate come inutilizzate da
#   LocaleKeyAnalyzer.ps1, leggendo il report da key_report.txt.
#
# Funzioni principali:
#   - Legge le chiavi inutilizzate da key_report.txt (report_folder)
#   - Esegue un dry-run con anteprima delle chiavi da rimuovere
#   - Chiede conferma esplicita prima di applicare modifiche
#   - Corregge le virgole trailing dopo la rimozione
#   - Salva backup del file originale e delle chiavi rimosse
#
# Input (da config.json):
#   source_file   → file JSON da pulire
#   report_folder → cartella da cui leggere key_report.txt
#                   e dove salvare il backup delle chiavi rimosse
#
# Dipendenze:
#   Va eseguito DOPO LocaleKeyAnalyzer.ps1, che genera key_report.txt.
#
# Utilizzo:
#   Eseguire quando si vuole applicare la pulizia delle chiavi morte.
#   Verificare sempre il dry-run prima di confermare.
# ============================================================

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

$localePath     = Join-Path $projectRoot $config.source_file
$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)
$reportDir      = Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName
$backupDir      = Join-Path (Join-Path $projectRoot $config.backup_folder) $sourceBaseName
$unusedListPath = Join-Path $reportDir "key_report.txt"

if (-not (Test-Path $localePath)) {
    Write-Host "[ERROR] source_file not found: $localePath"
    exit 1
}

if (-not (Test-Path $unusedListPath)) {
    Write-Host "[ERROR] key_report.txt not found at: $unusedListPath"
    Write-Host "[INFO]  Run LocaleKeyAnalyzer.ps1 first"
    exit 1
}

New-Item -ItemType Directory -Force -Path $backupDir  | Out-Null
New-Item -ItemType Directory -Force -Path $reportDir  | Out-Null

Write-Host "[INFO] Source file  : $localePath"
Write-Host "[INFO] Key report   : $unusedListPath"
Write-Host "[INFO] Backup dir   : $backupDir"

# ============================================================
# 4. LOAD UNUSED KEYS FROM REPORT
# ============================================================

$unusedKeys = Get-Content $unusedListPath

$startIndex = $unusedKeys.IndexOf("UNUSED KEYS")
if ($startIndex -lt 0) {
    Write-Host "[ERROR] 'UNUSED KEYS' section not found in key_report.txt"
    exit 1
}

$endIndex = $unusedKeys.IndexOf("KEY USAGE MAP")
if ($endIndex -lt 0) { $endIndex = $unusedKeys.Count }

$unusedKeys = $unusedKeys[($startIndex + 1)..($endIndex - 1)] |
    Where-Object {
        $_.Trim() -ne "" -and
        $_ -notmatch '^-{2,}$' -and
        $_ -notmatch '^=+'
    }

$unusedSet = @{}
foreach ($k in $unusedKeys) {
    $key = $k.Trim()
    if ($key.Length -gt 0) { $unusedSet[$key] = $true }
}

Write-Host "[INFO] Unused keys loaded: $($unusedSet.Count)"

# ============================================================
# 5. BUILD CANDIDATE DIFF (DRY RUN — NO MODIFICHE)
# ============================================================

$lines = Get-Content $localePath

$candidateKeptLines    = @()
$candidateRemovedLines = @()

foreach ($line in $lines) {

    if ($line -match '^\s*"([^"]+)"\s*:') {

        $key = $matches[1]

        if ($unusedSet.ContainsKey($key)) {
            $candidateRemovedLines += $line
            continue
        }
    }

    $candidateKeptLines += $line
}

# ============================================================
# 6. DRY RUN PREVIEW
# ============================================================

Write-Host "`n[PLAN SUMMARY]"
Write-Host "Keys to remove : $($candidateRemovedLines.Count)"
Write-Host "Keys to keep   : $($candidateKeptLines.Count - 2)"

$preview = $candidateRemovedLines | Select-Object -First 20

Write-Host "`nSample keys to remove:"
foreach ($l in $preview) {
    if ($l -match '"([^"]+)"\s*:') {
        Write-Host "  - $($matches[1])"
    }
}

if ($candidateRemovedLines.Count -gt 20) {
    Write-Host "  ... and $($candidateRemovedLines.Count - 20) more"
}

# ============================================================
# 7. CONFIRMATION
# ============================================================

$confirm = Read-Host "`nApply changes? (Y/N)"

if ($confirm -ne "Y") {
    Write-Host "[ABORTED] No changes applied"
    exit 0
}

# ============================================================
# 8. FIX TRAILING COMMAS
# ============================================================

$keptLines = $candidateKeptLines

for ($i = 0; $i -lt $keptLines.Count; $i++) {

    if ($keptLines[$i] -match '^\s*".*":') {

        $hasNextKey = $false

        for ($j = $i + 1; $j -lt $keptLines.Count; $j++) {

            if ($keptLines[$j] -match '^\s*".*":') {
                $hasNextKey = $true
                break
            }

            if ($keptLines[$j] -match '^\s*}$') { break }
        }

        if ($hasNextKey) {
            if ($keptLines[$i] -notmatch ',\s*$') {
                $keptLines[$i] += ","
            }
        } else {
            $keptLines[$i] = $keptLines[$i] -replace ',\s*$', ''
        }
    }
}

# ============================================================
# 9. BACKUP
# ============================================================

$timestamp      = Get-Date -Format "yyyyMMdd"
$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($localePath)
$sourceExt      = [System.IO.Path]::GetExtension($localePath)

# calcola numero progressivo per pre_clean
$counter = 1
while (Test-Path (Join-Path $backupDir "${sourceBaseName}_pre_clean_${counter}_${timestamp}${sourceExt}")) {
    $counter++
}

# backup file originale
$localeBackup = Join-Path $backupDir "${sourceBaseName}_pre_clean_${counter}_${timestamp}${sourceExt}"
Copy-Item $localePath $localeBackup

# backup chiavi rimosse
$removedBackup = Join-Path $backupDir "${sourceBaseName}_unused_removed_${counter}_${timestamp}.json"
$candidateRemovedLines | Set-Content $removedBackup -Encoding UTF8

# ============================================================
# 10. WRITE CLEAN FILE
# ============================================================

$keptLines | Set-Content $localePath -Encoding UTF8

# ============================================================
# 11. FINAL REPORT
# ============================================================

Write-Host "`n[OK] Clean completed"
Write-Host "Removed keys  : $($candidateRemovedLines.Count)"
Write-Host "Original bak  : $localeBackup"
Write-Host "Removed bak   : $removedBackup"