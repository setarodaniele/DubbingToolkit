# ==========================================================
# Extract-Placeholders.ps1
# ==========================================================
# Scopo:
#   Analizza il file locale sorgente (source_file da config.json)
#   ed estrae tutti i placeholder presenti nelle stringhe.
#
# Funzioni principali:
#   - Scansiona tutte le chiavi del file JSON di traduzione
#   - Identifica i placeholder tramite regex unificata
#     ({0}, {}, {file_name}, {lang}, ecc.)
#   - Costruisce una mappa completa:
#       * frequenza globale dei placeholder
#       * associazione placeholder → chiavi
#       * associazione chiave → placeholder
#       * classificazione tipologica
#
# Output (in report_folder\<nome_file_sorgente>\):
#   - placeholder_map.json → dati strutturati per pipeline
#   - placeholder_map.txt  → report leggibile per analisi manuale
#
# Input (da config.json):
#   source_file      → file JSON da analizzare
#   placeholder_map  → path output placeholder_map.json
#   report_folder    → cartella base dei report
#
# Utilizzo:
#   Va eseguito quando il file sorgente viene modificato.
#   Serve a rigenerare lo stato dei placeholder prima della traduzione.
#   Va eseguito dopo la fase di pulizia (Fix, Validate, Clean).
# ==========================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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

$inputFile      = Join-Path $projectRoot $config.source_file
$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)
$reportDir      = Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName
$outputFile     = Join-Path $reportDir "placeholder_map.json"

if (-not (Test-Path $inputFile)) {
    Write-Host "[ERROR] source_file not found: $inputFile"
    exit 1
}

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

Write-Host "[INFO] Source file  : $inputFile"
Write-Host "[INFO] Output file  : $outputFile"

# =========================
# 4. LOAD JSON
# =========================

$json = Get-Content $inputFile -Raw | ConvertFrom-Json

# =========================
# 5. STRUTTURE DATI
# =========================

$globalUsage        = @{}
$keyMap             = @{}
$placeholderToKeys  = @{}

$totalKeys          = 0
$totalPlaceholders  = 0

# regex unica ufficiale
$regex = "\{\d+\}|\{\}|\{[a-zA-Z_][a-zA-Z0-9_]*(?::[^}]+)?\}"

# =========================
# 6. SCANSIONE CHIAVI JSON
# =========================

foreach ($prop in $json.PSObject.Properties) {

    $key   = $prop.Name
    $value = [string]$prop.Value
    $totalKeys++

    $found = [regex]::Matches($value, $regex) | ForEach-Object { $_.Value }

    if ($found.Count -gt 0) {

        $keyMap[$key]       = $found
        $totalPlaceholders += $found.Count

        foreach ($ph in $found) {

            if (-not $globalUsage.ContainsKey($ph)) { $globalUsage[$ph] = 0 }
            $globalUsage[$ph]++

            if (-not $placeholderToKeys.ContainsKey($ph)) { $placeholderToKeys[$ph] = @() }
            $placeholderToKeys[$ph] += $key
        }
    }
}

# =========================
# 7. CLASSIFICAZIONE TIPI
# =========================

$types = @{
    BRACE_INDEX = @()
    C_STYLE     = @()
    MUSTACHE    = @()
}

foreach ($ph in $globalUsage.Keys) {

    if ($ph -match "^\{\d+\}$")   { $types.BRACE_INDEX += $ph }
    elseif ($ph -match "^%\w$")   { $types.C_STYLE     += $ph }
    elseif ($ph -match "^\{\{.*\}\}$") { $types.MUSTACHE += $ph }
}

# =========================
# 8. COSTRUZIONE OUTPUT JSON
# =========================

$result = @{
    summary = @{
        total_keys         = $totalKeys
        total_placeholders = $totalPlaceholders
    }
    global_usage        = $globalUsage
    key_map             = $keyMap
    types               = $types
    placeholder_to_keys = $placeholderToKeys
}

$jsonOutput = $result | ConvertTo-Json -Depth 10

# =========================
# 9. WRITE JSON FILE
# =========================

$jsonOutput | Out-File -Encoding UTF8 $outputFile

Write-Output "[INFO] Mapping completata"
Write-Output "[INFO] File output      : $outputFile"
Write-Output "[INFO] Keys analizzate  : $totalKeys"
Write-Output "[INFO] Placeholder      : $totalPlaceholders"

# =========================
# 10. HUMAN READABLE REPORT
# =========================

$infoFile   = Join-Path $reportDir "placeholder_map.txt"
$infoReport = @()

$infoReport += "=================================================="
$infoReport += " PLACEHOLDER REPORT"
$infoReport += "=================================================="
$infoReport += ""
$infoReport += "INPUT FILE        : $inputFile"
$infoReport += "TOTAL KEYS        : $totalKeys"
$infoReport += "TOTAL PLACEHOLDERS: $totalPlaceholders"
$infoReport += ""
$infoReport += "------------------------------"
$infoReport += "GLOBAL USAGE"
$infoReport += "------------------------------"

foreach ($item in ($globalUsage.GetEnumerator() | Sort-Object Value -Descending)) {
    $infoReport += "$($item.Key) => $($item.Value)"
}

$infoReport += ""
$infoReport += "------------------------------"
$infoReport += "KEY MAP (sample max 30)"
$infoReport += "------------------------------"

$counter = 0
foreach ($item in $keyMap.GetEnumerator()) {
    $infoReport += "$($item.Key) => $($item.Value -join ', ')"
    $counter++
    if ($counter -ge 30) { break }
}

$infoReport += ""
$infoReport += "------------------------------"
$infoReport += "TYPE SUMMARY"
$infoReport += "------------------------------"

foreach ($t in $types.Keys) {
    $infoReport += "$t : $($types[$t].Count)"
}

$infoReport -join "`n" | Out-File -Encoding UTF8 $infoFile

Write-Output "[INFO] Text report      : $infoFile"
