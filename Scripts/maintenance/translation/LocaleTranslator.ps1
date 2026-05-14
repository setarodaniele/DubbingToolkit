# ============================================================
# LocaleTranslator.ps1
# ============================================================
# Scopo:
#   Traduce il file JSON sorgente (source_file da config.json)
#   nelle lingue configurate in target_languages, usando
#   Google Cloud Translate API.
#
# Funzioni principali:
#   - Carica le credenziali Google Cloud da file esterno
#   - Carica la libreria Protect-Placeholders.ps1 via dot-sourcing
#   - Maschera i placeholder prima della traduzione e li ripristina
#     dopo, usando la placeholder_map generata da Extract-Placeholders.ps1
#   - Gestisce una cache su disco per evitare ritraduzioni inutili
#   - Valida il file sorgente prima della traduzione
#   - Controlla l'integrità dei placeholder dopo la traduzione
#   - Salva i file tradotti in output_folder
#
# Input (da config.json):
#   source_file       → file JSON sorgente da tradurre
#   target_languages  → lingue di destinazione (es. ["en"])
#   placeholder_map   → path della mappa placeholder (relativo a projectRoot)
#   report_folder     → cartella base dei report (per sottocartella sourceBaseName)
#   output_folder     → cartella output file tradotti
#   use_cache         → abilita/disabilita la cache
#   cache_dir         → cartella della cache
#   cache_file        → nome file della cache
#
# Dipendenze:
#   - Protect-Placeholders.ps1  (dot-sourced, stessa cartella)
#   - Extract-Placeholders.ps1  (deve essere eseguito prima per generare placeholder_map)
#   - credentials\GoogleCloudTranslate.json (relativo a projectRoot)
#
# Utilizzo:
#   Va eseguito dopo l'intera fase di pulizia e dopo Extract-Placeholders.ps1
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
    Write-Host "[ERROR] Project root not found (Locale folder missing)"
    exit 1
}

# ============================================================
# 2. CONFIG + CREDENTIALS
# ============================================================

$configPath = Join-Path $PSScriptRoot "config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "[ERROR] Missing config.json at $configPath"
    exit 1
}

$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json

$credentialsPath = Join-Path $projectRoot "credentials\GoogleCloudTranslate.json"

if (-not (Test-Path $credentialsPath)) {
    Write-Host "[ERROR] Missing Google credentials at $credentialsPath"
    exit 1
}

$googleCred = Get-Content $credentialsPath -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not $googleCred.google_translate_api_key) {
    Write-Host "[ERROR] Missing google_translate_api_key in credentials file"
    exit 1
}

if (-not $googleCred.project_id) {
    Write-Host "[ERROR] Missing project_id in credentials file"
    exit 1
}

$script:apiKey = $googleCred.google_translate_api_key

# ============================================================
# 3. LOAD PLACEHOLDER LIBRARY
# ============================================================

$protectScript = Join-Path $PSScriptRoot "Protect-Placeholders.ps1"

if (-not (Test-Path $protectScript)) {
    Write-Host "[ERROR] Missing Protect-Placeholders.ps1 at $protectScript"
    exit 1
}

. $protectScript

Write-Host "[INFO] Placeholder library loaded"

# ============================================================
# 4. BUILD TOKEN MAP
# ============================================================

$sourceBaseName = [System.IO.Path]::GetFileNameWithoutExtension($config.source_file)

if ($config.placeholder_map) {
    $placeholderMapPath = Join-Path $projectRoot $config.placeholder_map
} else {
    $placeholderMapPath = Join-Path (Join-Path (Join-Path $projectRoot $config.report_folder) $sourceBaseName) "placeholder_map.json"
}

Write-Host "[INFO] Placeholder map   : $placeholderMapPath"

if (-not (Test-Path $placeholderMapPath)) {
    Write-Host "[ERROR] Missing placeholder map at $placeholderMapPath"
    Write-Host "[INFO]  Run Extract-Placeholders.ps1 first"
    exit 1
}

$phEngine = Build-TokenMap -PlaceholderMapPath $placeholderMapPath

if (-not $phEngine) {
    Write-Host "[ERROR] Failed to build token map"
    exit 1
}

Write-Host "[INFO] Token map built: $($phEngine.Count) tokens"

$tokenMap   = $phEngine.TokenMap
$reverseMap = $phEngine.ReverseMap

# ============================================================
# 5. INPUT / OUTPUT PATHS
# ============================================================

$sourceFile = Join-Path $projectRoot $config.source_file

$outputDir = Join-Path $PSScriptRoot $config.output_folder
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# ============================================================
# 6. SAFETY CHECK + LOAD SOURCE
# ============================================================

if (-not (Test-Path $sourceFile)) {
    Write-Host "[ERROR] Missing source file: $sourceFile"
    exit 1
}

Write-Host "[INFO] Loading source file: $sourceFile"

$sourceJson = Get-Content $sourceFile -Encoding UTF8 | ConvertFrom-Json

# ============================================================
# 6.1 VALIDATOR PRE-TRANSLATION
# ============================================================

function Validate-Source {
    param($json)

    $errors = @()

    foreach ($prop in $json.PSObject.Properties) {
        $key   = $prop.Name
        $value = $prop.Value

        if ($value -match '\s{2,}') { $errors += "$key | MULTIPLE_SPACES" }
        if ($value -match '\w#\d{3}#' -or $value -match '#\d{3}#\w') {
            $errors += "$key | PLACEHOLDER_ATTACHED"
        }
    }

    return $errors
}

$validationErrors = Validate-Source $sourceJson

if ($validationErrors.Count -gt 0) {
    Write-Host ""
    Write-Host "=========== VALIDATION FAILED ==========="
    foreach ($e in $validationErrors) { Write-Host $e }
    Write-Host "========================================="
    exit 1
}

# ============================================================
# 7. DISK CACHE INIT
# ============================================================

$cacheDir = Join-Path $projectRoot $config.cache_dir

if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    Write-Host "[INFO] Cache directory created: $cacheDir"
}

$cacheFile     = Join-Path $cacheDir $config.cache_file
$cacheDebugLog = Join-Path $cacheDir "cache_debug.log"

function Write-CacheLog {
    param([string]$level, [string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $cacheDebugLog -Value "[$timestamp][$level] $message" -Encoding UTF8
}

Add-Content -Path $cacheDebugLog -Value "" -Encoding UTF8
Write-CacheLog "INFO" "SESSION START"
Write-CacheLog "INFO" "Cache file path: $cacheFile"

$script:sessionStart     = Get-Date
$script:translationCache = @{}
$script:cacheDirty       = $false

# ============================================================
# CACHE LOAD
# ============================================================

if (Test-Path $cacheFile) {
    try {
        $jsonObj = Get-Content $cacheFile -Raw -Encoding UTF8 | ConvertFrom-Json

        foreach ($prop in $jsonObj.PSObject.Properties) {
            $script:translationCache[$prop.Name] = $prop.Value
        }

        Write-CacheLog "INFO" "Cache loaded. Entries=$($script:translationCache.Count)"
    }
    catch {
        Write-CacheLog "WARN" "Cache corrupted"
        $script:translationCache = @{}
    }
}

# ============================================================
# CACHE KEY
# ============================================================

function Get-CacheKey {
    param([string]$lang, [string]$text)

    if ([string]::IsNullOrWhiteSpace($text)) { return $null }

    $sha1  = [System.Security.Cryptography.SHA1]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash  = $sha1.ComputeHash($bytes)
    $hex   = ([BitConverter]::ToString($hash) -replace '-', '').ToLower()

    return "$lang|$hex"
}

# ============================================================
# TRANSLATION ENGINE
# ============================================================

function Invoke-RealTranslationEngine {
    param($text, $lang)

    $maxRetries = 3
    $attempt    = 0

    Write-CacheLog "API-SEND" "$lang | $text"

    while ($attempt -lt $maxRetries) {
        try {
            $body     = "q=$([uri]::EscapeDataString($text))&target=$lang&format=text"
            $uri      = "https://translation.googleapis.com/language/translate/v2?key=$($script:apiKey)"
            $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
            $translated = $response.data.translations[0].translatedText

            Write-CacheLog "API-RECV" "$translated"

            # aggiorna cache e segna come dirty
            $keyCache = Get-CacheKey $lang $text
            $script:translationCache[$keyCache] = $translated
            $script:cacheDirty = $true

            return $translated
        }
        catch {
            $attempt++
            Write-CacheLog "WARN" "API fail attempt=$attempt"
            Start-Sleep -Seconds (2 * $attempt)
        }
    }

    Write-CacheLog "ERROR" "API failed after $maxRetries attempts"
    return $text
}

# ============================================================
# TRANSLATE
# ============================================================

function Translate-Text {
    param([string]$text, [string]$lang)

    if ([string]::IsNullOrWhiteSpace($text)) { return $text }

    $keyCache = Get-CacheKey $lang $text

    if ($config.use_cache -and $script:translationCache.ContainsKey($keyCache)) {
        return $script:translationCache[$keyCache]
    }

    return Invoke-RealTranslationEngine $text $lang
}

# ============================================================
# 8. PROCESS
# ============================================================

$totalKeys = ($sourceJson.PSObject.Properties | Measure-Object).Count

foreach ($lang in $config.target_languages) {

    $translatedCount = 0
    $identicalCount  = 0
    $integrityErrors = 0
    $cacheHitCount   = 0
    $cacheMissCount  = 0

    $warningsList  = @()
    $identicalList = @()

    $output = [ordered]@{}

    foreach ($prop in $sourceJson.PSObject.Properties) {

        $key   = $prop.Name
        $value = $prop.Value

        # MASK
        $maskedValue = Invoke-MaskPlaceholders -Text $value -TokenMap $tokenMap

        # TRANSLATE
        $keyCache = Get-CacheKey $lang $maskedValue
        $wasHit   = ($config.use_cache -and $script:translationCache.ContainsKey($keyCache))

        $translatedMasked = Translate-Text $maskedValue $lang

        if ($wasHit) { $cacheHitCount++ } else { $cacheMissCount++ }

        # RESTORE
        $translated = Invoke-RestorePlaceholders -Text $translatedMasked -ReverseMap $reverseMap

        # IDENTICAL CHECK
        $normOriginal   = ($value      -replace '\s+', ' ').Trim()
        $normTranslated = ($translated -replace '\s+', ' ').Trim()

        if ($normOriginal -eq $normTranslated) {
            $identicalCount++
            $identicalList += $key
        } else {
            $translatedCount++
        }

        # PLACEHOLDER INTEGRITY CHECK
        $originalPH   = [regex]::Matches($value,      '\{[^{}]+\}')
        $translatedPH = [regex]::Matches($translated, '\{[^{}]+\}')

        $hasWarning  = $false
        $warningType = ""

        if ($originalPH.Count -ne $translatedPH.Count) {
            $hasWarning  = $true
            $warningType = "PLACEHOLDER_COUNT_MISMATCH"
        }

        if (-not $hasWarning) {
            for ($i = 0; $i -lt $originalPH.Count; $i++) {
                if ($originalPH[$i].Value -ne $translatedPH[$i].Value) {
                    $hasWarning  = $true
                    $warningType = "PLACEHOLDER_ORDER_MISMATCH"
                    break
                }
            }
        }

        if ($hasWarning) {
            $integrityErrors++
            $warningsList += "$key | $warningType"
            Write-Host "[WARN] $key | $warningType"
        }

        $output[$key] = $translated
    }

    # SALVA OUTPUT
    $outputFile = Join-Path $outputDir "$lang.json"
    $output | ConvertTo-Json -Depth 10 | Set-Content $outputFile -Encoding UTF8
    Write-Host "[INFO] Output saved: $outputFile"

    # LOG SUMMARY
    Write-CacheLog "SUMMARY" "Lang=$lang total=$totalKeys translated=$translatedCount identical=$identicalCount hits=$cacheHitCount misses=$cacheMissCount errors=$integrityErrors"

    Write-CacheLog "IDENTICAL" "START"
    foreach ($i in $identicalList) { Write-CacheLog "IDENTICAL" $i }
    Write-CacheLog "IDENTICAL" "END"

    Write-CacheLog "WARNINGS" "START"
    foreach ($w in $warningsList) { Write-CacheLog "WARNINGS" $w }
    Write-CacheLog "WARNINGS" "END"
}

# ============================================================
# 9. CACHE SAVE
# ============================================================

if ($script:cacheDirty -eq $true) {
    $script:translationCache | ConvertTo-Json -Depth 10 | Set-Content $cacheFile -Encoding UTF8
    Write-CacheLog "INFO" "Cache saved. Entries=$($script:translationCache.Count)"
}

# ============================================================
# END
# ============================================================

Write-CacheLog "INFO" "SESSION END"
Write-Host "[INFO] Translation completed."