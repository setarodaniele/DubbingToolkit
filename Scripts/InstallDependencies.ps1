# ==================================================================
# INSTALLDEPENDENCIES.PS1 - DEPENDENCIES INSTALLATION FOR AUTOMATIC DUBBING
# Updated for multiple requirements files, cache disabled, Torch CPU/CUDA auto
# ==================================================================

param(
    [Parameter(Mandatory=$true)]
    [string[]]$RequirementsFiles,  # Array di file requirements da installare in sequenza
    [Parameter(Mandatory=$true)]
    [string]$VenvPath
)


# ==================================================================
#  1 Determine root folder. Load localization messages from settings.json
# ==================================================================

$RootFolder = Split-Path $PSScriptRoot -Parent
$LocaleFolder = Join-Path $RootFolder 'Locale'

# Legge la lingua dall'impostazione centralizzata
$SettingFile = Join-Path $RootFolder 'Settings\settings.json'
$Settings = Get-Content $SettingFile -Encoding UTF8 | ConvertFrom-Json
$interface_langKey = $Settings.interface_lang

# Carica i messaggi corrispondenti
$MessagesFile = Join-Path $LocaleFolder ("Active\$interface_langKey.json")
$Messages = Get-Content $MessagesFile -Encoding UTF8 | ConvertFrom-Json

Write-Host $Messages.InstallDependencies_Starting -ForegroundColor Blue

# ----------------------------------------
# 2 Attiva l'ambiente virtuale
# ----------------------------------------
& "$VenvPath\Scripts\Activate.ps1"
# Disabilita messaggio di aggiornamento pip
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

# ----------------------------------------
# 3 Lettura pacchetti già installati
# ----------------------------------------
$InstalledNowRaw = & "$VenvPath\Scripts\pip.exe" list --format=freeze
$InstalledNow = @{}
foreach ($line in $InstalledNowRaw) {
    $line = $line.Trim()
    if ($line -match '^(?<name>[^=]+)==(?<ver>.+)$') {
        $pkgNameNorm = $matches.name.ToLower() -replace '[-_]', ''
        $InstalledNow[$pkgNameNorm] = $matches.ver
    }
}

# ----------------------------------------
# 4 Funzione di installazione pacchetto singolo
# ----------------------------------------
function Install-Package-DabbingToolkit($pkg, $extraIndexLink) {
    Write-Host ($Messages.InstallingPackage -f $Index, $Total, $pkg) -ForegroundColor Cyan

    $InstallArgs = @(
        "--disable-pip-version-check"
        $pkg
    )

    if ($extraIndexLink) {
        $InstallArgs += "-f"
        $InstallArgs += $extraIndexLink
    }

    try {
        & "$VenvPath\Scripts\pip.exe" install @InstallArgs

        # --- DEBUG: mostra il pacchetto corrente
        Write-Host "DEBUG: pkg dal requirements.txt -> '$pkg'" -ForegroundColor Yellow

        # --- Lettura installati
        $InstalledNowRaw = & "$VenvPath\Scripts\pip.exe" list --format=freeze
        $InstalledNow = $InstalledNowRaw -split "`r?`n" | ForEach-Object { $_.Trim() }

        # --- Normalizzazione nome pacchetto
        $pkgName = $pkg.Split("==")[0].ToLower()
        $Found = $InstalledNow | Where-Object {
            $installedName = ($_ -split "==")[0].ToLower()
            $installedName = $installedName -replace '[-_]', ''
            $normalizedPkg = $pkgName -replace '[-_]', ''
            $installedName -eq $normalizedPkg
        }

        if ($Found) {
            Write-Host "DEBUG: Pacchetto trovato -> $($Found -join ', ')" -ForegroundColor Green
        } else {
            Write-Host "DEBUG: Pacchetto NON trovato" -ForegroundColor Red
        }

    } catch {
        Write-Host ($Messages.PackageFailed -f $pkg) -ForegroundColor Red
        exit 1
    }
}

# ----------------------------------------
# 5 Ciclo su ogni file requirements
# ----------------------------------------
foreach ($ReqFile in $RequirementsFiles) {
    #Write-Host ("----------------------------------------") -ForegroundColor DarkGray
    Write-Host ($Messages.InstallDependencies_ProcessingRequirements -f $ReqFile) -ForegroundColor Blue

    # 5a. Lettura contenuto requirements
    $ReqContent = Get-Content $ReqFile | Where-Object {
        $_ -and $_ -notmatch '^\s*#' -and $_ -notmatch '^-f '
    } | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }

    # 5b. Costruzione lista pacchetti da installare confrontando con quelli già installati
    $ToInstall = @()
    foreach ($pkg in $ReqContent) {
        # Override Torch / TorchVision / Torchaudio in base a CUDA
        if ($pkg -match '^torch$') {
            $cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
            if (Test-Path $cudaPath) {
                $TorchSuffix = '+cu121'
            } else {
                $TorchSuffix = '+cpu'
            }
            $pkgFull = "torch==2.1.0$TorchSuffix"
            $Global:TorchSuffixForOthers = $TorchSuffix
        } elseif ($pkg -match '^torchvision$') {
            $pkgFull = "torchvision==0.16.0$Global:TorchSuffixForOthers"
        } elseif ($pkg -match '^torchaudio$') {
            $pkgFull = "torchaudio==2.1.0$Global:TorchSuffixForOthers"
        } else {
            $pkgFull = $pkg
        }

        # Normalizzazione nome pacchetto
        $pkgNameNorm = $pkgFull.Split("==")[0].ToLower() -replace '[-_]', ''
        $pkgVer = ($pkgFull -split "==")[1]

        # Verifica se già installato e versione corretta
        if (-not ($InstalledNow.ContainsKey($pkgNameNorm)) -or $InstalledNow[$pkgNameNorm] -ne $pkgVer) {
            $ToInstall += $pkgFull
        }
    }

    $Total = $ToInstall.Count
    if ($Total -eq 0) {
        Write-Host $Messages.InstallDependencies_AllDependenciesAlreadyInstalled -ForegroundColor Green
        continue
    }

    # 5c. Ciclo di installazione pacchetti mancanti
    $Index = 0
    foreach ($pkg in $ToInstall) {
        $Index++

        # Link PyTorch se necessario
        if ($pkg -match '^torch' -or $pkg -match '^torchvision' -or $pkg -match '^torchaudio') {
            $ExtraLink = 'https://download.pytorch.org/whl/torch_stable.html'
        } else {
            $ExtraLink = $null
        }

        Install-Package-DabbingToolkit $pkg $ExtraLink
    }
}

Write-Host $Messages.InstallDependencies_AllDependenciesInstalled -ForegroundColor Green
Write-Host $Messages.DependenciesFinished -ForegroundColor Blue