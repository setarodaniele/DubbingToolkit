# ==================================================================
# Logging.psm1 Module
# ==================================================================

$modulePath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module (Join-Path $modulePath "Messages.psm1")

function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Key,

        [ValidateSet("INFO","WARN","ERROR")]
        [string]$Level = "INFO",

        [string[]]$Args = @()
    )

    # RISOLUZIONE QUI (punto centrale)
    $Message = Get-Message $Key $Args

    switch ($Level) {
        "INFO"  { $color = "Gray" }
        "WARN"  { $color = "Yellow" }
        "ERROR" { $color = "Red" }
        default { $color = "DarkGray" }
    }

    Write-Host "[$Level] $Message" -ForegroundColor $color
}