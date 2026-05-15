# ============================================================
# DUBBING TOOLKIT - INSTALLER BUILD SYSTEM
# ============================================================
# Version: 1.3 (interactive menu + explicit -Test parameter)
#
# Purpose:
#   Generates a clean, deterministic installation package
#   inside "build_payload" for Inno Setup packaging.
#
# ------------------------------------------------------------
# BUILD MODES
# ------------------------------------------------------------
# TEST MODE (default):
#   - Lightweight build for rapid iteration
#   - Excludes heavy components (Python runtime, ffmpeg, voices)
#   - Uses additional rules from: build_exclude_test.json
#   - No confirmation prompt
#
# PRODUCTION MODE:
#   - Full build including all dependencies
#   - Requires confirmation prompt before proceeding
#
# DRY-RUN MODE:
#   - Simulates packaging without writing any files
#   - Prints file count and total size, then exits
#   - No confirmation prompt
#
# ------------------------------------------------------------
# PIPELINE OVERVIEW
# ------------------------------------------------------------
# [00] Mode selection (interactive menu if no parameter given)
# [01] Load configuration (include / exclude / empty dirs)
# [02] Preview rule summary
# [02.5] Dry-run file simulation (if -DryRun, exits here)
# [03] User confirmation gate (PRODUCTION only)
# [04] Reset build output directory
# [05] Create empty runtime directories
# [06] Execute file packaging:
#      - Full copy mode
#      - Sanitized copy mode (filtered rules)
# [07] Finalize build output
#
# ------------------------------------------------------------
# USAGE
# ------------------------------------------------------------
# Interactive menu:        .\build.ps1
# Test build (explicit):   .\build.ps1 -Test
# Production build:        .\build.ps1 -Production
# Dry run only:            .\build.ps1 -DryRun
#
# ------------------------------------------------------------
# RULE MODEL
# ------------------------------------------------------------
# INCLUDE:
#   Defines what is packaged into the installer.
#
# EXCLUDE:
#   Global blacklist applied during all copy modes.
#
# EXCLUDE_TEST:
#   Additional blacklist applied ONLY in test mode.
#
# PROTECTED:
#   Paths copied verbatim — exclude rules are bypassed.
#   Use for third-party distributions (e.g. Python runtime).
#
# EMPTY_DIRS:
#   Runtime folders created empty (structure only).
#
# SANITIZED COPY:
#   Selective copy with per-item filename whitelist.
#
# ------------------------------------------------------------
# SECURITY MODEL (CRITICAL)
# ------------------------------------------------------------
# - Credentials must NEVER be shipped as real files.
# - Only template credential files are included.
# - Sensitive runtime data is generated post-install.
#
# ------------------------------------------------------------
# OUTPUT CONTRACT
# ------------------------------------------------------------
# - build_payload is always fully regenerated
# - no manual edits inside build_payload are allowed
# - output must be deterministic and repeatable
#
# ============================================================

param(
    [switch]$DryRun,
    [switch]$Test,
    [switch]$Production
)

# ============================================================
# [00] MODE SELECTION
# ============================================================

# Interactive menu if no argument was passed
if (-not $DryRun -and -not $Test -and -not $Production) {
    Write-Host ""
    Write-Host "======================================="
    Write-Host " DUBBING TOOLKIT - BUILD SYSTEM"
    Write-Host "======================================="
    Write-Host ""
    Write-Host "  1  DRY-RUN     (simulazione, nessun file creato)"
    Write-Host "  2  TEST        (build leggera, senza Python/ffmpeg/voices)"
    Write-Host "  3  PRODUCTION  (build completa)"
    Write-Host ""
    $choice = Read-Host "Seleziona modalità [1/2/3]"

    switch ($choice) {
        "1" { $DryRun = $true }
        "2" { }
        "3" { $Production = $true }
        default {
            Write-Host "Scelta non valida. Annullato."
            exit 1
        }
    }
}

# Default: TEST (explicit -Test or neither -Production nor -DryRun)
if (-not $Test -and -not $Production -and -not $DryRun) {
    $Test = $true
} elseif ($Production) {
    $Test = $false
}

Write-Host ""
Write-Host "======================================="

if ($DryRun) {
    Write-Host " MODALITÀ DRY-RUN (simulazione, nessun file creato)"
} elseif ($Test) {
    Write-Host " MODALITÀ TEST (BUILD LEGGERA)"
    Write-Host " Esclusi: Python runtime, ffmpeg, voices"
} else {
    Write-Host " MODALITÀ PRODUZIONE (BUILD COMPLETA)"
}

Write-Host "======================================="
Write-Host ""

# ============================================================
# [01] INIT - CONFIGURATION
# ============================================================

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $root
$buildPath = Join-Path $root "build_payload"

$includeFile      = Join-Path $root "build_include.json"
$excludeFile      = Join-Path $root "build_exclude.json"
$excludeTestFile  = Join-Path $root "build_exclude_test.json"
$emptyDirsFile    = Join-Path $root "build_empty_dirs.json"
$protectedFile    = Join-Path $root "build_protected.json"

$include   = Get-Content $includeFile   | ConvertFrom-Json
$exclude   = Get-Content $excludeFile   | ConvertFrom-Json
$emptyDirs = Get-Content $emptyDirsFile | ConvertFrom-Json

# Merge exclude rules (TEST only)
$excludeTest = @()
if ($Test -and (Test-Path $excludeTestFile)) {
    $excludeTest = Get-Content $excludeTestFile | ConvertFrom-Json
    $exclude += $excludeTest
}

$protectedRaw = if (Test-Path $protectedFile) { Get-Content $protectedFile | ConvertFrom-Json } else { @() }
$protected    = @($protectedRaw | ForEach-Object { [System.IO.Path]::GetFullPath((Join-Path $projectRoot $_)) })

# ============================================================
# HELPER - PROTECTED PATH CHECK
# ============================================================

function Test-IsProtected([string]$path, [string[]]$protectedList) {
    foreach ($p in $protectedList) {
        $base = $p.TrimEnd('\')
        if ($path -eq $base -or $path.StartsWith($base + '\')) { return $true }
    }
    return $false
}

# ============================================================
# [02] PREVIEW - RULE SUMMARY
# ============================================================

Write-Host "=== BUILD SYSTEM ===`n"

if ($DryRun) { Write-Host "[DRY RUN MODE - no files will be written]`n" }

Write-Host "--- INCLUDE RULES ---"
foreach ($item in $include) {
    Write-Host "[INCLUDE] $($item.source) -> $($item.dest) ($($item.type))"
}

Write-Host "`n--- EXCLUDE RULES ---"
foreach ($rule in $exclude) {
    Write-Host "[EXCLUDE] $rule"
}

Write-Host "`n--- EMPTY DIRECTORIES ---"
foreach ($dir in $emptyDirs) {
    Write-Host "[EMPTY] $dir"
}

Write-Host "`n--- PROTECTED PATHS (exclude rules bypassed) ---"
if ($protectedRaw.Count -eq 0) {
    Write-Host "(none)"
} else {
    foreach ($path in $protectedRaw) {
        Write-Host "[PROTECTED] $path"
    }
}

# ============================================================
# [02.5] DRY RUN - FILE SIMULATION
# ============================================================

if ($DryRun) {

    Write-Host "`n=== FILE SIMULATION ===`n"

    $totalFiles = 0
    $totalBytes = 0

    function Test-IsExcluded($filePath, $excludeRules) {
        foreach ($rule in $excludeRules) {
            if ($filePath -like "*$rule*") { return $true }
        }
        return $false
    }

    foreach ($item in $include) {

        $source = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $item.source))
        $type = $item.type

        Write-Host "[ITEM] $($item.source)  ($type)"

        # Test-mode: item-level skip, overrides protected
        if ($Test -and $excludeTest.Count -gt 0) {
            $itemSkipped = $false
            foreach ($rule in $excludeTest) {
                if ($source -like "*$rule*") { $itemSkipped = $true; break }
            }
            if ($itemSkipped) {
                Write-Host "  [EXCLUDED TEST - item skipped]"
                continue
            }
        }

        if (!(Test-Path $source)) {
            Write-Host "  [MISSING] $source"
            continue
        }

        if ($type -eq "file") {
            if (!(Test-IsExcluded $source $exclude)) {
                $size = [System.IO.FileInfo]::new($source).Length
                Write-Host ("  [FILE] {0}  ({1:N2} MB)" -f (Split-Path $source -Leaf), ($size / 1MB))
                $totalFiles++
                $totalBytes += $size
            } else {
                Write-Host "  [EXCLUDED] $(Split-Path $source -Leaf)"
            }
            continue
        }

        $files = [System.IO.Directory]::GetFiles($source, "*", [System.IO.SearchOption]::AllDirectories)
        $itemFiles = 0
        $itemBytes = 0

        foreach ($file in $files) {

            $excluded = if (Test-IsProtected $source $protected) { $false } else { Test-IsExcluded $file $exclude }

            if ($type -eq "sanitized" -and $item.include) {
                $fileName = [System.IO.Path]::GetFileName($file)
                $allowed = $false
                foreach ($pattern in $item.include) {
                    if ($fileName -like $pattern) { $allowed = $true; break }
                }
                # Whitelist overrides global excludes: if explicitly allowed, force include
                $excluded = -not $allowed
            }

            if (-not $excluded) {
                $itemFiles++
                $itemBytes += [System.IO.FileInfo]::new($file).Length
            }
        }

        Write-Host ("  -> {0} files  |  {1:N2} MB" -f $itemFiles, ($itemBytes / 1MB))
        $totalFiles += $itemFiles
        $totalBytes += $itemBytes
    }

    Write-Host "`n=== DRY RUN SUMMARY ==="
    Write-Host ("Total files  : {0}" -f $totalFiles)
    Write-Host ("Total size   : {0:N1} MB" -f ($totalBytes / 1MB))
    Write-Host "`n[DRY RUN COMPLETE - no files written]"
    exit 0
}

# ============================================================
# [03] USER CONFIRMATION GATE (PRODUCTION only)
# ============================================================

if (-not $Test) {
    $confirm = Read-Host "`nProceed with build? (Y/N)"
    if ($confirm -ne "Y") {
        Write-Host "Build cancelled."
        exit 0
    }
}

# ============================================================
# [04] RESET BUILD OUTPUT
# ============================================================

if (Test-Path $buildPath) {
    Remove-Item $buildPath -Recurse -Force
    Write-Host ""
    Write-Host "======================================="
    Write-Host " build_payload ELIMINATA"
    Write-Host "======================================="
    Write-Host ""
    Start-Sleep -Seconds 5
}

New-Item -ItemType Directory -Path $buildPath | Out-Null

# ============================================================
# [05] CREATE EMPTY DIRECTORIES
# ============================================================

foreach ($dir in $emptyDirs) {

    $path = Join-Path $buildPath $dir

    if (!(Test-Path $path)) {
        Write-Host "[CREATE EMPTY] $dir"
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# ============================================================
# [06] BUILD PROCESS
# ============================================================

$totalFiles = 0
$totalBytes = 0

foreach ($item in $include) {

    $source = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $item.source))
    $dest = Join-Path $buildPath $item.dest
    $type = $item.type

    # Test-mode: item-level skip, overrides protected
    if ($Test -and $excludeTest.Count -gt 0) {
        $itemSkipped = $false
        foreach ($rule in $excludeTest) {
            if ($source -like "*$rule*") { $itemSkipped = $true; break }
        }
        if ($itemSkipped) {
            Write-Host "[EXCLUDED TEST] $($item.source)"
            continue
        }
    }

    if (!(Test-Path $source)) {
        Write-Host "[MISSING] $source"
        continue
    }

    Write-Host "`n[PROCESS] $source -> $dest ($type)"
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    if ($type -eq "file") {
        $isExcluded = $false
        foreach ($rule in $exclude) {
            if ($source -like "*$rule*") { $isExcluded = $true; break }
        }
        if ($isExcluded) {
            Write-Host "[EXCLUDED] $(Split-Path $source -Leaf)"
            continue
        }
        Copy-Item $source (Join-Path $dest (Split-Path $source -Leaf)) -Force
        $totalFiles++
        $totalBytes += [System.IO.FileInfo]::new($source).Length
        continue
    }

    $files = [System.IO.Directory]::GetFiles($source, "*", [System.IO.SearchOption]::AllDirectories)
    $sourceIsProtected = Test-IsProtected $source $protected

    foreach ($file in $files) {

        $excluded = $false

        if (-not $sourceIsProtected) {
            foreach ($rule in $exclude) {
                if ($file -like "*$rule*") { $excluded = $true; break }
            }
        }

        if ($type -eq "sanitized" -and $item.include) {
            $fileName = [System.IO.Path]::GetFileName($file)
            $allowed = $false

            foreach ($pattern in $item.include) {
                if ($fileName -like $pattern) { $allowed = $true; break }
            }

            # Whitelist overrides global excludes: if explicitly allowed, force include
            $excluded = -not $allowed
        }

        if ($excluded) { continue }

        $relative = $file.Substring($source.TrimEnd('\').Length)
        $target = Join-Path $dest $relative
        $targetDir = Split-Path $target -Parent

        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

        Copy-Item $file $target -Force
        $totalFiles++
        $totalBytes += [System.IO.FileInfo]::new($file).Length
    }
}

# ============================================================
# [07] BUILD COMPLETE
# ============================================================
Write-Host "`n=== BUILD COMPLETE ==="
Write-Host ("Total files  : {0}" -f $totalFiles)
Write-Host ("Total size   : {0:N1} MB" -f ($totalBytes / 1MB))
Write-Host ""
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host " PASSO SUCCESSIVO:" -ForegroundColor Yellow
Write-Host " Esegui build_manifest.ps1 per aggiornare" -ForegroundColor Yellow
Write-Host " il manifest e rigenerare payload_sections.iss" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host ""