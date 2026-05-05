# ============================================================
# Protect-Placeholders.ps1
# ============================================================
# Scopo:
#   Libreria di funzioni per la protezione dei placeholder
#   durante la traduzione. Va caricata via dot-sourcing
#   da LocaleTranslator.ps1. NON eseguire direttamente.
#
# Funzioni esportate:
#   Build-TokenMap             → costruisce tokenMap e reverseMap
#                                dalla placeholder_map.json
#   Invoke-MaskPlaceholders    → maschera i placeholder in una stringa
#                                sostituendoli con token #NNN#
#   Invoke-RestorePlaceholders → ripristina i placeholder originali
#                                dai token #NNN#
#
# Dipendenze:
#   placeholder_map.json generato da Extract-Placeholders.ps1
# ============================================================

# ============================================================
# BUILD-TOKENMAP
# Costruisce tokenMap e reverseMap dalla placeholder_map
# ============================================================

function Build-TokenMap {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PlaceholderMapPath
    )

    if (-not (Test-Path $PlaceholderMapPath)) {
        Write-Host "[ERROR] Placeholder map not found: $PlaceholderMapPath"
        return $null
    }

    $placeholderMap = Get-Content $PlaceholderMapPath -Raw -Encoding UTF8 | ConvertFrom-Json

    $tokenMap   = [ordered]@{}
    $reverseMap = [ordered]@{}
    $counter    = 1

    $keyMap = $placeholderMap.key_map

    foreach ($key in $keyMap.PSObject.Properties.Name) {

        $value = $keyMap.$key

        if ($value -is [string]) {
            $placeholders = @($value)
        }
        elseif ($value -is [System.Array]) {
            $placeholders = $value
        }
        else {
            continue
        }

        foreach ($ph in $placeholders) {
            if ($tokenMap.Contains($ph)) { continue }
            $token = [char]0x27E6 + ("{0:D3}" -f $counter) + [char]0x27E7
            $tokenMap[$ph]      = $token
            $reverseMap[$token] = $ph
            $counter++
        }
    }

    return [PSCustomObject]@{
        TokenMap   = $tokenMap
        ReverseMap = $reverseMap
        Count      = $tokenMap.Count
    }
}

# ============================================================
# INVOKE-MASKPLACEHOLDERS
# Maschera i placeholder in una stringa
# ============================================================

function Invoke-MaskPlaceholders {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [Parameter(Mandatory = $true)]
        [System.Collections.Specialized.OrderedDictionary]$TokenMap
    )

    foreach ($ph in $TokenMap.Keys) {
        $Text = $Text.Replace([string]$ph, [string]$TokenMap[$ph])
    }

    return $Text
}

# ============================================================
# INVOKE-RESTOREPLACEHOLDERS
# Ripristina i placeholder in una stringa
# ============================================================

function Invoke-RestorePlaceholders {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [Parameter(Mandatory = $true)]
        [System.Collections.Specialized.OrderedDictionary]$ReverseMap
    )

    foreach ($token in $ReverseMap.Keys) {
        $Text = $Text.Replace([string]$token, [string]$ReverseMap[$token])
    }

    return $Text
}