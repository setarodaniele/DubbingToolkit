# ============================================================
# LocaleKeyAnalyzer.ps1
# ============================================================
# Scopo:
#   Analizza il file locale sorgente (source_file da config.json)
#   e determina quali chiavi sono effettivamente utilizzate
#   nel codice sorgente del progetto.
#
# Funzioni principali:
#   - Carica le chiavi dal file JSON sorgente
#   - Esclude le chiavi di sistema (lang, lang_*)
#   - Rileva chiavi duplicate nel JSON grezzo
#   - Scansiona i file .ps1, .psm1, .py nelle cartelle configurate
#     cercando riferimenti alle chiavi con quattro pattern:
#       CASE A: object access    → messages.CHIAVE
#       CASE B: string literal   → "CHIAVE" o 'CHIAVE'
#       CASE C: getattr literal  → getattr(messages, "CHIAVE")
#       CASE D: getattr f-string → getattr(messages, f"PREFIX_{var}")
#                                  marca come usate tutte le chiavi
#                                  che iniziano con PREFIX_
#   - Produce due report nella report_folder:
#       * key_report.txt          → chiavi usate/inutilizzate + file mapping
#       * unused_key_clusters.txt → chiavi inutilizzate raggruppate per prefisso
#
# Input (da config.json):
#   source_file      → file JSON da analizzare
#   scan_paths       → cartelle del progetto da scansionare
#   exclude_patterns → pattern di percorsi da escludere
#   report_folder    → cartella di output dei report
#
# Utilizzo:
#   Va eseguito prima di Clean-LocaleUnusedKeys.ps1.
#   Rigenerare ogni volta che il codice sorgente o it.json cambiano.
# ============================================================

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

$localeFile      = Join-Path $projectRoot $config.source_file
$sourceBaseName  = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)
$reportDir       = Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName
$scanPaths       = $config.scan_paths | ForEach-Object { Join-Path $projectRoot $_ }
$excludePatterns = $config.exclude_patterns

if (-not (Test-Path $localeFile)) {
    Write-Host "[ERROR] source_file not found: $localeFile"
    exit 1
}

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

Write-Host "[INFO] Source file : $localeFile"
Write-Host "[INFO] Report dir  : $reportDir"

# ============================================================
# 4. LOAD JSON + KEY EXTRACTION
# ============================================================

Write-Host "`n[INFO] Loading keys..."

$json = Get-Content $localeFile -Encoding UTF8 | ConvertFrom-Json

$keys = @()

foreach ($prop in $json.PSObject.Properties) {
    $keys += $prop.Name
}

# Escludi chiavi di sistema runtime (lang, lang_*)
$keys = $keys | Where-Object {
    $_ -notmatch '^(?i)lang$' -and
    $_ -notmatch '^(?i)lang_'
}

$keysSet = @{}
foreach ($k in $keys) { $keysSet[$k] = $true }

# ============================================================
# 5. DUPLICATE DETECTION (RAW JSON)
# ============================================================

Write-Host "[INFO] Checking duplicate keys..."

$rawJson = Get-Content $localeFile -Raw

$rawKeys = [regex]::Matches(
    $rawJson,
    '^\s*"([^"]+)"\s*:',
    'Multiline'
) | ForEach-Object { $_.Groups[1].Value }

$duplicates = $rawKeys | Group-Object | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    Write-Host "[WARNING] Duplicate keys found:"
    foreach ($d in $duplicates) {
        Write-Host "  - $($d.Name) (x$($d.Count))"
    }
} else {
    Write-Host "[OK] No duplicate keys"
}

# ============================================================
# 6. FILE COLLECTION
# ============================================================

Write-Host "`n[INFO] Scanning project files..."

$files = foreach ($path in $scanPaths) {

    if (-not (Test-Path $path)) { continue }

    Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {

        $extOk = $_.Extension -in @(".ps1", ".psm1", ".py")
        if (-not $extOk) { return $false }

        foreach ($pattern in $excludePatterns) {
            if ($_.FullName -match [regex]::Escape($pattern)) { return $false }
        }

        return $true
    }
}

$files = @($files)

Write-Host "[INFO] Files found: $($files.Count)"

foreach ($f in $files) {
    Write-Host "  - $($f.FullName)"
}

# ============================================================
# 7. CORE SCAN LOGIC
# ============================================================

$usedKeys  = @{}
$keyToFiles = @{}

foreach ($file in $files) {

    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }

    $filePath = $file.FullName

    # =========================
    # CASE C: getattr(messages, "KEY_LITERAL")
    # Rileva chiavi passate come stringa letterale a getattr
    # es: getattr(messages, "menu_voices_jump_prompt")
    # =========================
    $getAttrMatches = [regex]::Matches($content, 'getattr\s*\(\s*\w*messages?\w*\s*,\s*[''"]([^''"]+)[''"]')
    foreach ($m in $getAttrMatches) {
        $foundKey = $m.Groups[1].Value
        if ($keysSet.ContainsKey($foundKey)) {
            $usedKeys[$foundKey] = $true
            if (-not $keyToFiles.ContainsKey($foundKey)) { $keyToFiles[$foundKey] = @() }
            if ($keyToFiles[$foundKey] -notcontains $filePath) {
                $keyToFiles[$foundKey] += $filePath
            }
        }
    }

    # =========================
    # CASE D: getattr(messages, f"PREFIX_{variable}")
    # Rileva prefissi dinamici nelle f-string di getattr
    # es: getattr(messages, f"LANG_{detected_lang}", ...)
    #     getattr(messages, f"INFO_Progetto_{k}", ...)
    # Marca come usate TUTTE le chiavi che iniziano con quel prefisso
    # =========================
    $getAttrFstringMatches = [regex]::Matches($content, 'getattr\s*\(\s*\w*messages?\w*\s*,\s*f[''"]([A-Za-z0-9_]+)_\{')
    foreach ($m in $getAttrFstringMatches) {
        $prefix = $m.Groups[1].Value + "_"
        foreach ($key in $keys) {
            if ($key.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $usedKeys[$key] = $true
                if (-not $keyToFiles.ContainsKey($key)) { $keyToFiles[$key] = @() }
                if ($keyToFiles[$key] -notcontains $filePath) {
                    $keyToFiles[$key] += $filePath
                }
            }
        }
    }

    foreach ($key in $keys) {

        # CASE A: messages.KEY / Messages.KEY / $messages.KEY / Messages().KEY / msgs.KEY
        $patternObjectAccess = "(?i)\b(messages?|msgs)\b\.?[()]*\.$([regex]::Escape($key))\b"

        if ($content -match $patternObjectAccess) {
            $usedKeys[$key] = $true
            if (-not $keyToFiles.ContainsKey($key)) { $keyToFiles[$key] = @() }
            $keyToFiles[$key] += $filePath
            continue
        }

        # CASE B: "KEY" o 'KEY' come stringa letterale
        $patternDouble = '"' + [regex]::Escape($key) + '"'
        $patternSingle = "'" + [regex]::Escape($key) + "'"

        if ($content -match $patternDouble -or $content -match $patternSingle) {
            $usedKeys[$key] = $true
            if (-not $keyToFiles.ContainsKey($key)) { $keyToFiles[$key] = @() }
            $keyToFiles[$key] += $filePath
        }
    }
}

# ============================================================
# 8. UNUSED KEYS CALCULATION
# ============================================================

$unused = @()

foreach ($key in $keys) {
    if (-not $usedKeys.ContainsKey($key)) {
        $unused += $key
    }
}

# ============================================================
# 9. CONSOLE REPORT
# ============================================================

Write-Host "`n=============================="
Write-Host "KEY ANALYSIS REPORT"
Write-Host "=============================="
Write-Host "Total keys (runtime) : $($keys.Count)"
Write-Host "Total keys (raw)     : $($rawKeys.Count)"
Write-Host "Used keys            : $($usedKeys.Count)"
Write-Host "Unused keys          : $($unused.Count)"
Write-Host "Files analyzed       : $($files.Count)"

# ============================================================
# 10. KEY REPORT FILE
# ============================================================

$reportPath = Join-Path $reportDir "key_report.txt"

$report = @()
$report += "TOTAL KEYS: $($keys.Count)"
$report += "USED KEYS: $($usedKeys.Count)"
$report += "UNUSED KEYS: $($unused.Count)"
$report += "FILES ANALYZED: $($files.Count)"
$report += ""
$report += "=============================="
$report += "UNUSED KEYS"
$report += "=============================="
$report += $unused -join "`n"
$report += ""
$report += "=============================="
$report += "KEY USAGE MAP"
$report += "=============================="

foreach ($k in $keyToFiles.Keys) {
    $report += ""
    $report += $k
    $report += ($keyToFiles[$k] -join "`n")
}

$report | Set-Content $reportPath -Encoding UTF8

Write-Host "[INFO] Key report saved to: $reportPath"

# ============================================================
# 11. CLUSTER REPORT FILE
# ============================================================

$clusterPath = Join-Path $reportDir "unused_key_clusters.txt"

$clusters = @{}

foreach ($key in $unused) {
    $cluster = ($key -split "_", 2)[0]
    if (-not $clusters.ContainsKey($cluster)) { $clusters[$cluster] = @() }
    $clusters[$cluster] += $key
}

$clusterReport = @()
$clusterReport += "=============================="
$clusterReport += "UNUSED KEYS - CLUSTER REPORT"
$clusterReport += "=============================="
$clusterReport += ""

foreach ($c in ($clusters.Keys | Sort-Object)) {
    $clusterReport += "[$c] ($($clusters[$c].Count))"
    $clusterReport += ($clusters[$c] | Sort-Object)
    $clusterReport += ""
}

$clusterReport | Set-Content $clusterPath -Encoding UTF8

Write-Host "[INFO] Cluster report saved to: $clusterPath"

# ============================================================
# 12. END
# ============================================================

Write-Host "[INFO] Analysis completed"