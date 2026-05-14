# ==================================================================
# Messages.psm1 Module
# ==================================================================

# Variabile interna al modulo
$script:Messages = $null

function Set-Messages {
    param(
        [Parameter(Mandatory=$true)]
        [object]$MessagesObject
    )

    $script:Messages = $MessagesObject
}

function Get-Message {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Key,
        [object[]]$Args = @()
    )

    if (-not $script:Messages) {
        return "Missing key: $Key"
    }

    # Caso Hashtable
    if ($script:Messages -is [hashtable]) {
        if (-not $script:Messages.ContainsKey($Key)) {
            return "Missing key: $Key"
        }
        $value = $script:Messages[$Key]
    }
    else {
        # Caso oggetto JSON
        if (-not $script:Messages.PSObject.Properties[$Key] -or -not $script:Messages.$Key) {
            return "Missing key: $Key"
        }
        $value = $script:Messages.$Key
    }

    if ($Args.Count -gt 0) {
        return ($value -f $Args)
    }

    return $value
}

Export-ModuleMember -Function Set-Messages, Get-Message