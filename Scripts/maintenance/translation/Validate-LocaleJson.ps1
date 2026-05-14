# ============================================================
# Validate-LocaleJson.ps1
# ============================================================
# Scopo:
#   Analizza la qualità strutturale delle stringhe nel file
#   locale sorgente (source_file da config.json) e segnala
#   anomalie senza modificare nulla.
#
# Controlli eseguiti:
#   - EMPTY_STRING         → stringa vuota
#   - ONLY_SPACES          → stringa composta solo da spazi
#   - LEADING_SPACE        → spazio iniziale non voluto
#   - TRAILING_SPACE       → spazio finale non voluto
#   - MULTIPLE_SPACES      → spazi multipli interni
#   - PLACEHOLDER_UNBALANCED → parentesi graffe { } non bilanciate
#   - EMPTY_PLACEHOLDER    → placeholder vuoto {} tracciato separatamente
#
# Output:
#   - report a console
#   - validate_locale_report.txt in report_folder
#
# Note:
#   Non modifica il JSON. Non esegue trasformazioni.
#   Usare come quality gate prima delle fasi di traduzione.
#
# Input (da config.json):
#   source_file   → file JSON da validare
#   report_folder → cartella dove salvare il report
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

$inputFile      = Join-Path $projectRoot $config.source_file
$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)
$reportDir      = Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName
$outputReport   = Join-Path $reportDir "validate_locale_report.txt"

if (-not (Test-Path $inputFile)) {
    Write-Host "[ERROR] source_file not found: $inputFile"
    exit 1
}

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

Write-Host "[INFO] Source file : $inputFile"
Write-Host "[INFO] Report file : $outputReport"

# ============================================================
# 4. LOAD JSON
# ============================================================

$json = Get-Content $inputFile -Raw | ConvertFrom-Json

# ============================================================
# 5. ISSUE TRACKING
# ============================================================

$totalKeys = 0

$issues = @{
    EMPTY_STRING             = @()
    ONLY_SPACES              = @()
    LEADING_SPACE            = @()
    TRAILING_SPACE           = @()
    MULTIPLE_SPACES          = @()
    PLACEHOLDER_UNBALANCED   = @()
    EMPTY_PLACEHOLDER        = @()
}

function Add-Issue($type, $key) {
    $issues[$type] += $key
}

# ============================================================
# 6. SCAN KEYS
# ============================================================

foreach ($prop in $json.PSObject.Properties) {

    $key   = $prop.Name
    $value = [string]$prop.Value
    $totalKeys++

    # 1. stringa vuota
    if ($value.Length -eq 0) {
        Add-Issue "EMPTY_STRING" $key
        continue
    }

    # 2. solo spazi
    if ($value -match '^\s+$') {
        Add-Issue "ONLY_SPACES" $key
        continue
    }

    # 3. leading space
    if ($value -match '^\s+') {
        Add-Issue "LEADING_SPACE" $key
    }

    # 4. trailing space
    if ($value -match '\s+$') {
        Add-Issue "TRAILING_SPACE" $key
    }

    # 5. spazi multipli interni
    if ($value -match '\s{2,}') {
        Add-Issue "MULTIPLE_SPACES" $key
    }

    # 6. parentesi graffe sbilanciate
    $openBraces  = ([regex]::Matches($value, "\{")).Count
    $closeBraces = ([regex]::Matches($value, "\}")).Count

    if ($openBraces -ne $closeBraces) {
        Add-Issue "PLACEHOLDER_UNBALANCED" $key
    }

    # 7. placeholder vuoti {}
    if ($value -match "\{\}") {
        Add-Issue "EMPTY_PLACEHOLDER" $key
    }
}

# ============================================================
# 7. CLEAN COUNT
# ============================================================

$problematicKeys = $issues.Keys |
    ForEach-Object { $issues[$_] } |
    Select-Object -Unique

$problematicCount = @($problematicKeys).Count
$cleanCount       = $totalKeys - $problematicCount

# ============================================================
# 8. BUILD REPORT
# ============================================================

$report = @()
$report += "=== VALIDATION REPORT ==="
$report += ""
$report += "Source : $inputFile"
$report += "Total keys : $totalKeys"
$report += ""
$report += "ISSUES FOUND:"
$report += ""

foreach ($k in $issues.Keys | Sort-Object) {
    if ($issues[$k].Count -gt 0) {
        $report += "[$k] ($($issues[$k].Count))"
        $report += ($issues[$k] -join "`n")
        $report += ""
    }
}

$report += "SUMMARY:"
$report += "  Clean        : $cleanCount"
$report += "  Problematic  : $problematicCount"

$finalReport = $report -join "`n"

# ============================================================
# 9. OUTPUT
# ============================================================

Write-Output $finalReport

$finalReport | Out-File -Encoding UTF8 $outputReport

Write-Host "`n[INFO] Report saved to: $outputReport"
