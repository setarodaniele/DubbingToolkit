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

# Initialize logging module
$psDir = Join-Path $RootFolder 'ps'
Import-Module (Join-Path $psDir 'Logging.psm1') -Force
Set-Messages $Messages

Write-Log "InstallDependencies_Starting"

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
    Write-Log "InstallingPackage" "INFO" @($Index, $Total, $pkg)

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
    } catch {
        Write-Log "PackageFailed" "ERROR" @($pkg)
        exit 1
    }
}

# ----------------------------------------
# 5 Ciclo su ogni file requirements
# ----------------------------------------
foreach ($ReqFile in $RequirementsFiles) {
    #Write-Host ("----------------------------------------") -ForegroundColor DarkGray
    Write-Log "InstallDependencies_ProcessingRequirements" "INFO" @($ReqFile)

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

Write-Log "DependenciesFinished"