<#
==============================================================================
build_manifest.ps1
Description : Generatore interattivo del manifest di classificazione per il
              payload di installazione di DubbingToolkit.
Input       : build_payload\ (primo livello + credentials\ un livello)
              InnoSetup\payload_manifest.json se esiste
Output      : InnoSetup\payload_manifest.json
Notes       : Eseguire da installer\ oppure da qualsiasi directory;
              usa $PSScriptRoot per i percorsi.
==============================================================================
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

$ScriptDir    = $PSScriptRoot
$PayloadDir   = Join-Path $ScriptDir "build_payload"
$ManifestDir  = Join-Path $ScriptDir "InnoSetup"
$ManifestPath = Join-Path $ManifestDir "payload_manifest.json"

# ==============================================================================
# 2. DEFAULT MANIFEST -- usato solo se payload_manifest.json non esiste ancora
# ==============================================================================

$DefaultEntries = @(
    # -- System: cartelle complete
    [ordered]@{ path="Installation"; type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Tools";        type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="core";         type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="locale";       type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="ps";           type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Scripts";      type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Settings";     type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Docs";         type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="voices";       type="system"; install=$true;  create_empty=$false; recursive=$true;  clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },

    # -- System: file singoli
    [ordered]@{ path="StartDubbing.bat";                            type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Readme.txt";                                  type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="Billing/tts_voices_cost.json";                type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },

    # -- System: file dentro credentials\
    [ordered]@{ path="credentials/azure_speech_credentials.template.json";  type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="credentials/google_speech_credentials.template.json"; type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },
    [ordered]@{ path="credentials/README.md";                               type="system"; install=$true;  create_empty=$false; recursive=$false; clean_on_upgrade=$true;  remove_on_uninstall=$true;  uninstall_prompt=$false },

    # -- User: credentials contenitore misto
    [ordered]@{ path="credentials"; type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group=$null; uninstall_conditional=$true },

    # -- User: workspace e dati di lavoro (gruppo work_files)
    [ordered]@{ path="Workspace";          type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="work_files"; uninstall_conditional=$false },
    [ordered]@{ path="Workspace/projects"; type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="work_files"; uninstall_conditional=$false },
    [ordered]@{ path="Logs";               type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="work_files"; uninstall_conditional=$false },

    # -- User: Billing contenitore (gruppo billing)
    [ordered]@{ path="Billing"; type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="billing"; uninstall_conditional=$false }
)

$GroupTemplates = [ordered]@{
    "work_files"  = [ordered]@{ type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="work_files"; uninstall_conditional=$false }
    "billing"     = [ordered]@{ type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group="billing";    uninstall_conditional=$false }
    "credentials" = [ordered]@{ type="user"; install=$false; create_empty=$true; recursive=$false; clean_on_upgrade=$false; remove_on_uninstall=$false; uninstall_prompt=$true; uninstall_prompt_default=$false; uninstall_prompt_group=$null;         uninstall_conditional=$true  }
}

# ==============================================================================
# 3. UTILITIES
# ==============================================================================

function Write-Header {
    param([string]$Text)
    $line = "-" * 62
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step { param([string]$t) Write-Host "  >> $t" -ForegroundColor DarkGray }
function Write-OK   { param([string]$t) Write-Host "  [OK] $t" -ForegroundColor Green }
function Write-Warn { param([string]$t) Write-Host "  [!]  $t" -ForegroundColor Yellow }
function Write-Err  { param([string]$t) Write-Host "  [X]  $t" -ForegroundColor Red }

function ConvertTo-OrderedHashtable {
    param($Object)
    if ($null -eq $Object) { return $null }
    $ht = [ordered]@{}
    foreach ($prop in $Object.PSObject.Properties) {
        $val = $prop.Value
        if ($val -is [System.Management.Automation.PSCustomObject]) {
            $val = ConvertTo-OrderedHashtable $val
        }
        $ht[$prop.Name] = $val
    }
    return $ht
}

function Load-Manifest {
    if (-not (Test-Path $ManifestPath)) { return $null }
    try {
        $raw  = Get-Content $ManifestPath -Raw -Encoding UTF8
        $json = $raw | ConvertFrom-Json
        $list = [System.Collections.Generic.List[object]]::new()
        foreach ($e in @($json.entries)) {
            $list.Add((ConvertTo-OrderedHashtable $e))
        }
        return $list
    }
    catch {
        Write-Warn "Impossibile leggere il manifest esistente: $_"
        return $null
    }
}

function Save-Manifest {
    param($Entries)
    $manifest = [ordered]@{
        version        = "1.0"
        generated      = (Get-Date -Format "yyyy-MM-dd")
        schema_version = "1.0"
        entries        = @($Entries)
    }
    if (-not (Test-Path $ManifestDir)) {
        New-Item -ItemType Directory -Path $ManifestDir | Out-Null
    }
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $ManifestPath -Encoding UTF8
    Write-OK "Manifest salvato: $ManifestPath ($($Entries.Count) voci)"
}

function Get-PayloadItems {
    $items = [System.Collections.Generic.List[PSCustomObject]]::new()
    foreach ($item in (Get-ChildItem -Path $PayloadDir -Depth 0)) {
        $items.Add([PSCustomObject]@{ RelPath = $item.Name; IsDir = $item.PSIsContainer })
    }
    $credDir = Join-Path $PayloadDir "credentials"
    if (Test-Path $credDir) {
        foreach ($item in (Get-ChildItem -Path $credDir -Depth 0)) {
            $items.Add([PSCustomObject]@{ RelPath = "credentials/$($item.Name)"; IsDir = $item.PSIsContainer })
        }
    }
    $billingDir = Join-Path $PayloadDir "Billing"
    if (Test-Path $billingDir) {
        foreach ($item in (Get-ChildItem -Path $billingDir -Depth 0)) {
            $items.Add([PSCustomObject]@{ RelPath = "Billing/$($item.Name)"; IsDir = $item.PSIsContainer })
        }
    }
    return $items
}

function Ask-YesNo {
    param([string]$Prompt, [bool]$Default = $false)
    $hint = if ($Default) { "S/n" } else { "s/N" }
    $valid = $false
    $result = $Default
    while (-not $valid) {
        Write-Host "       $Prompt [$hint]: " -ForegroundColor Yellow -NoNewline
        $raw = Read-Host
        if ($raw -eq "")           { $result = $Default; $valid = $true }
        elseif ($raw -match '^[sS1]$') { $result = $true;    $valid = $true }
        elseif ($raw -match '^[nN0]$') { $result = $false;   $valid = $true }
        else { Write-Host "       Risposta non valida. Usa s oppure n." -ForegroundColor Red }
    }
    return $result
}

function Ask-Bounded {
    param([string]$Prompt, [int]$Min, [int]$Max)
    $result = -1
    while ($result -lt $Min -or $result -gt $Max) {
        Write-Host "       $Prompt [$Min-$Max]: " -ForegroundColor Yellow -NoNewline
        $raw = Read-Host
        if ($raw -match '^\d+$') {
            $n = [int]$raw
            if ($n -ge $Min -and $n -le $Max) { $result = $n }
            else { Write-Host "       Valore fuori range." -ForegroundColor Red }
        }
        else { Write-Host "       Inserire un numero." -ForegroundColor Red }
    }
    return $result
}

function Ask-MenuChar {
    param([string]$Prompt, [string[]]$Valid)
    $validStr = $Valid -join "/"
    $ch = ""
    while ($Valid -notcontains $ch) {
        Write-Host "       $Prompt [$validStr]: " -ForegroundColor Yellow -NoNewline
        $raw = Read-Host
        $ch  = $raw.Trim().ToUpper()
        if ($Valid -notcontains $ch) {
            Write-Host "       Scelta non valida." -ForegroundColor Red
            $ch = ""
        }
    }
    return $ch
}

function Build-SystemEntry {
    param([string]$Path, [bool]$IsDir)
    return [ordered]@{
        path                = $Path
        type                = "system"
        install             = $true
        create_empty        = $false
        recursive           = $IsDir
        clean_on_upgrade    = $true
        remove_on_uninstall = $true
        uninstall_prompt    = $false
    }
}

function Build-UserStandaloneEntry {
    param([string]$Path, [bool]$IsDir)
    return [ordered]@{
        path                     = $Path
        type                     = "user"
        install                  = $false
        create_empty             = $IsDir
        recursive                = $false
        clean_on_upgrade         = $false
        remove_on_uninstall      = $false
        uninstall_prompt         = $true
        uninstall_prompt_default = $false
        uninstall_prompt_group   = $null
        uninstall_conditional    = $false
    }
}

function Build-ManualEntry {
    param([string]$Path, [bool]$IsDir)
    Write-Host ""
    Write-Host "       Inserimento manuale campo per campo:" -ForegroundColor DarkCyan

    $typeKey = Ask-MenuChar "type [S=system / U=user]" @("S", "U")
    $type    = if ($typeKey -eq "S") { "system" } else { "user" }

    $e = [ordered]@{ path = $Path; type = $type }

    $e.install             = Ask-YesNo "install?"             ($type -eq "system")
    $e.create_empty        = Ask-YesNo "create_empty?"        $false
    $e.recursive           = Ask-YesNo "recursive?"           ($IsDir -and $type -eq "system")
    $e.clean_on_upgrade    = Ask-YesNo "clean_on_upgrade?"    ($type -eq "system")
    $e.remove_on_uninstall = Ask-YesNo "remove_on_uninstall?" ($type -eq "system")
    $e.uninstall_prompt    = Ask-YesNo "uninstall_prompt?"    $false

    if ($e.uninstall_prompt) {
        $e.uninstall_prompt_default = Ask-YesNo "uninstall_prompt_default?" $false
        Write-Host "       uninstall_prompt_group (invio=null | work_files / billing / credentials): " -ForegroundColor Yellow -NoNewline
        $grp = Read-Host
        $e.uninstall_prompt_group = if ($grp.Trim() -eq "") { $null } else { $grp.Trim() }
        $e.uninstall_conditional  = Ask-YesNo "uninstall_conditional?" $false
    }

    return $e
}

function Invoke-ClassifyItem {
    param([string]$ItemPath, [bool]$IsDir)

    $kind = if ($IsDir) { "CARTELLA" } else { "FILE" }
    Write-Host ""
    Write-Host "  +----------------------------------------------------------+" -ForegroundColor Magenta
    Write-Host "  |  Nuovo: $ItemPath ($kind)" -ForegroundColor Magenta
    Write-Host "  +----------------------------------------------------------+" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "       [S]  System   - installato e aggiornato automaticamente" -ForegroundColor White
    Write-Host "       [U]  User     - cartella vuota, dati utente, non sovrascritta" -ForegroundColor White
    Write-Host "       [G]  Gruppo   - copia template di un gruppo esistente" -ForegroundColor White
    Write-Host "       [M]  Manuale  - inserisci ogni campo individualmente" -ForegroundColor White
    Write-Host ""

    $choice = Ask-MenuChar "Classificazione" @("S", "U", "G", "M")

    $entry = $null

    switch ($choice) {
        "S" {
            $entry = Build-SystemEntry -Path $ItemPath -IsDir $IsDir
            Write-OK "Classificato: System (recursive=$($entry.recursive))"
        }
        "U" {
            $entry = Build-UserStandaloneEntry -Path $ItemPath -IsDir $IsDir
            Write-OK "Classificato: User standalone"
        }
        "G" {
            $sep  = "  " + ([string][char]0x2500) * 53
            $gKeys = @($GroupTemplates.Keys)
            Write-Host ""
            Write-Host "  LEGENDA GRUPPI DISPONIBILI:" -ForegroundColor DarkCyan
            Write-Host $sep -ForegroundColor DarkGray
            Write-Host "  [1] work_files" -ForegroundColor White
            Write-Host "      Tipo        : user" -ForegroundColor Gray
            Write-Host "      Upgrade     : non toccata - i dati utente vengono preservati" -ForegroundColor Gray
            Write-Host "      Disinstall  : gestita dal checkbox `"File di lavoro`"" -ForegroundColor Gray
            Write-Host "                    (Workspace, progetti, log, ecc.)" -ForegroundColor Gray
            Write-Host $sep -ForegroundColor DarkGray
            Write-Host "  [2] billing" -ForegroundColor White
            Write-Host "      Tipo        : user" -ForegroundColor Gray
            Write-Host "      Upgrade     : non toccata - i dati di fatturazione vengono preservati" -ForegroundColor Gray
            Write-Host "      Disinstall  : gestita dal checkbox `"Dati di fatturazione`"" -ForegroundColor Gray
            Write-Host $sep -ForegroundColor DarkGray
            Write-Host "  [3] credentials" -ForegroundColor White
            Write-Host "      Tipo        : user" -ForegroundColor Gray
            Write-Host "      Upgrade     : non toccata - le credenziali utente vengono preservate" -ForegroundColor Gray
            Write-Host "      Disinstall  : gestita dal checkbox `"Credenziali e chiavi API`"" -ForegroundColor Gray
            Write-Host "                    eliminazione condizionale solo se presenti file utente" -ForegroundColor Gray
            Write-Host $sep -ForegroundColor DarkGray
            Write-Host ""
            $gIdx      = (Ask-Bounded "Scegli gruppo" 1 $gKeys.Count) - 1
            $groupName = $gKeys[$gIdx]
            $tmpl      = $GroupTemplates[$groupName]
            $entry     = [ordered]@{ path = $ItemPath }
            foreach ($k in $tmpl.Keys) { $entry[$k] = $tmpl[$k] }
            Write-OK "Aggiunto al gruppo '$groupName'"
        }
        "M" {
            $entry = Build-ManualEntry -Path $ItemPath -IsDir $IsDir
            Write-OK "Classificato: manuale"
        }
    }

    if ($IsDir -and ($choice -eq "S" -or $choice -eq "U")) {
        $uniform = Ask-YesNo ("Il contenuto della cartella $([char]0xE8) tutto dello stesso tipo?") $true
        if ($uniform) {
            $entry.recursive = $true
            return @($entry)
        }
        else {
            $entry.recursive = $false
            $physPath = Join-Path $PayloadDir $ItemPath
            $result   = [System.Collections.Generic.List[object]]::new()
            $result.Add($entry)
            if (Test-Path $physPath) {
                foreach ($child in (Get-ChildItem -Path $physPath -Depth 0)) {
                    $childRelPath = "$ItemPath/$($child.Name)"
                    $childEntries = @(Invoke-ClassifyItem -ItemPath $childRelPath -IsDir $child.PSIsContainer)
                    foreach ($e in $childEntries) { $result.Add($e) }
                }
            }
            return $result.ToArray()
        }
    }

    return @($entry)
}

# ==============================================================================
# 4. ISS GENERATOR
# ==============================================================================

function Build-IssPayload {
    param($Entries)

    $issPath = Join-Path $ManifestDir "payload_sections.iss"
    $out     = [System.Collections.Generic.List[string]]::new()

    $filesEntries     = @($Entries | Where-Object { $_["install"]             -eq $true })
    $dirsEntries      = @($Entries | Where-Object { $_["create_empty"]        -eq $true })
    $uninstallEntries = @($Entries | Where-Object { $_["remove_on_uninstall"] -eq $true })

    # [Files]
    $out.Add("[Files]")
    foreach ($e in $filesEntries) {
        $p   = ($e["path"]) -replace "/", "\"
        $rec = [bool]$e["recursive"]
        if ($rec) {
            $srcDir = Join-Path $PayloadDir $p
            $hasFiles = (Test-Path $srcDir) -and
                        ([System.IO.Directory]::GetFiles($srcDir, "*", [System.IO.SearchOption]::AllDirectories).Count -gt 0)
            if (-not $hasFiles) {
                Write-Warn "Saltato (directory vuota o assente nel payload): $p"
                continue
            }
            $out.Add("Source: `"..\build_payload\$p\*`"; DestDir: `"{app}\$p`"; Flags: recursesubdirs createallsubdirs ignoreversion")
        } elseif ($p -like "*\*") {
            $srcFile = Join-Path $PayloadDir $p
            if (-not (Test-Path $srcFile)) {
                Write-Warn "Saltato (file assente nel payload): $p"
                continue
            }
            $parent = Split-Path $p -Parent
            $out.Add("Source: `"..\build_payload\$p`"; DestDir: `"{app}\$parent`"; Flags: ignoreversion")
        } else {
            $srcFile = Join-Path $PayloadDir $p
            if (-not (Test-Path $srcFile)) {
                Write-Warn "Saltato (file assente nel payload): $p"
                continue
            }
            $out.Add("Source: `"..\build_payload\$p`"; DestDir: `"{app}`"; Flags: ignoreversion")
        }
    }
    $out.Add("Source: `"assets\DubbingToolkit_Studio.ico`";    DestDir: `"{app}\assets`"; Flags: ignoreversion")
    $out.Add("Source: `"assets\DubbingToolkit_Workspace.ico`"; DestDir: `"{app}\assets`"; Flags: ignoreversion")
    $out.Add("")

    # [Dirs]
    $out.Add("[Dirs]")
    foreach ($e in $dirsEntries) {
        $p = ($e["path"]) -replace "/", "\"
        $out.Add("Name: `"{app}\$p`"")
    }
    $out.Add("")

    # [UninstallDelete]
    $out.Add("[UninstallDelete]")
    foreach ($e in $uninstallEntries) {
        $p    = ($e["path"]) -replace "/", "\"
        $leaf = Split-Path $p -Leaf
        if ($leaf -like "*.*") {
            $out.Add("Type: files;          Name: `"{app}\$p`"")
        } else {
            $out.Add("Type: filesandordirs; Name: `"{app}\$p`"")
        }
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($issPath, $out, $utf8NoBom)

    return [PSCustomObject]@{
        FilesCount     = $filesEntries.Count + 2
        DirsCount      = $dirsEntries.Count
        UninstallCount = $uninstallEntries.Count
    }
}

# ==============================================================================
# 5. CORE LOGIC
# ==============================================================================

function Invoke-ManifestBuilder {

    if (-not (Test-Path $PayloadDir)) {
        Write-Err "build_payload\ non trovato: $PayloadDir"
        exit 1
    }

    $existing = Load-Manifest
    $entries  = [System.Collections.Generic.List[object]]::new()

    if ($null -eq $existing) {
        $n = $DefaultEntries.Count
        Write-Step "Nessun manifest trovato - caricamento $n default di riferimento."
        foreach ($e in $DefaultEntries) { $entries.Add($e) }
    }
    else {
        $manifestDate = ""
        try { $manifestDate = (Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json).generated } catch {}

        $decision = ""
        while ($decision -eq "") {
            Write-Host ""
            Write-Step "Manifest esistente trovato ($($existing.Count) voci) - $manifestDate"
            Write-Host "     [C]  Carica  - usa il manifest esistente come base" -ForegroundColor White
            Write-Host "     [R]  Reset   - ignora il manifest esistente e riparte dai default" -ForegroundColor White
            Write-Host ""
            $choice = Ask-MenuChar "Scelta" @("C", "R")

            if ($choice -eq "C") {
                $decision = "load"
            }
            else {
                Write-Host ""
                Write-Warn "ATTENZIONE: il manifest esistente verra' sovrascritto."
                $confirm = Ask-MenuChar "Sei sicuro?" @("S", "N")
                if ($confirm -eq "S") { $decision = "reset" }
            }
        }

        if ($decision -eq "load") {
            $n = $existing.Count
            Write-Step "Manifest esistente caricato ($n voci)."
            foreach ($e in $existing) { $entries.Add($e) }
        }
        else {
            $n = $DefaultEntries.Count
            Write-Step "Reset - caricamento $n default di riferimento."
            foreach ($e in $DefaultEntries) { $entries.Add($e) }
        }
    }

    Write-Step "Scansione $PayloadDir ..."
    $payloadItems = Get-PayloadItems
    Write-Step "Trovati $($payloadItems.Count) elementi nel payload."

    if ($decision -eq "load") {
        $physicalPaths = @{}
        foreach ($item in $payloadItems) { $physicalPaths[$item.RelPath] = $true }
        $orphans = @($entries | Where-Object { -not $physicalPaths.ContainsKey($_["path"]) })
        if ($orphans.Count -gt 0) {
            Write-Host ""
            Write-Warn "Elementi nel manifest non trovati in build_payload ($($orphans.Count)):"
            foreach ($o in $orphans) { Write-Host "     - $($o['path'])" -ForegroundColor White }
            Write-Host ""
            $removeOrphans = Ask-YesNo "Vuoi rimuoverli automaticamente dal manifest?" $false
            if ($removeOrphans) {
                $orphanPaths = @{}
                foreach ($o in $orphans) { $orphanPaths[$o["path"]] = $true }
                $filtered = [System.Collections.Generic.List[object]]::new()
                foreach ($e in $entries) {
                    if (-not $orphanPaths.ContainsKey($e["path"])) { $filtered.Add($e) }
                }
                $entries = $filtered
                Write-OK "Rimossi $($orphans.Count) elementi orfani dal manifest"
            }
            else {
                Write-Warn "Attenzione: elementi orfani nel manifest - la compilazione InnoSetup potrebbe fallire"
            }
        }
    }

    $index = @{}
    foreach ($e in $entries) { $index[$e.path] = $true }

    $confirmed  = 0
    $classified = 0

    $newItems = @($payloadItems | Where-Object { -not $index.ContainsKey($_.RelPath) })
    if ($newItems.Count -gt 0) {
        Write-Host ""
        Write-Step "Elementi nuovi trovati ($($newItems.Count)):"
        foreach ($item in $newItems) {
            $kind = if ($item.IsDir) { "CARTELLA" } else { "FILE" }
            Write-Host "     - $($item.RelPath)  ($kind)" -ForegroundColor White
        }
        Write-Host ""
        Write-Step "Inizio classificazione..."
    }

    foreach ($item in $payloadItems) {
        if ($index.ContainsKey($item.RelPath)) {
            Write-OK "Confermato: $($item.RelPath)"
            $confirmed++
        }
        else {
            $newEntries = $null
            while ($null -eq $newEntries) {
                try {
                    $newEntries = @(Invoke-ClassifyItem -ItemPath $item.RelPath -IsDir $item.IsDir)
                }
                catch {
                    Write-Err "Errore durante la classificazione: $_ - riprovo."
                    $newEntries = $null
                }
            }
            foreach ($e in $newEntries) {
                $entries.Add($e)
                $index[$e["path"]] = $true
            }
            $classified++
        }
    }

    Write-Host ""
    Write-Step "Confermati: $confirmed | Nuovi classificati: $classified"
    return $entries
}

# ==============================================================================
# 5b. CLEANUP ISS UPDATER
# ==============================================================================

function Update-CleanupInIss {
    param($Entries)

    $IssPath = Join-Path $ManifestDir "DubbingToolkit_setup.iss"

    $folders = @($Entries | Where-Object {
        $_["type"] -eq "system" -and
        [bool]$_["clean_on_upgrade"] -and
        [System.IO.Path]::GetExtension($_["path"]) -eq ""
    } | ForEach-Object {
        $leaf = Split-Path (($_["path"]) -replace "/", "\") -Leaf
        "  AppFolders.Add('$leaf');"
    })

    $count = $folders.Count

    if (-not (Test-Path $IssPath)) {
        $addLines = $folders -join "`r`n"
        $newContent = @"
[Setup]
; da completare

[Languages]
; da completare

[CustomMessages]
; da completare

; ============================================================
; PAYLOAD (generato automaticamente da build_manifest.ps1)
; ============================================================
#include "payload_sections.iss"

[Icons]
; da completare

[Run]
; da completare

[Code]

// ------------------------------------------------------------
// [08.03] PULIZIA CARTELLE APP (aggiornamento)
// ------------------------------------------------------------
procedure FillAppFolders(AppFolders: TStringList);
begin
// ##CLEANUP_BEGIN##
$addLines
// ##CLEANUP_END##
end;

procedure CleanAppFolders(InstallDir: String);
var
  AppFolders: TStringList;
  i:          Integer;
  FolderPath: String;
begin
  AppFolders := TStringList.Create;
  try
    FillAppFolders(AppFolders);
    for i := 0 to AppFolders.Count - 1 do
    begin
      FolderPath := InstallDir + '\' + AppFolders[i];
      if DirExists(FolderPath) then
        DelTree(FolderPath, True, True, True);
    end;
  finally
    AppFolders.Free;
  end;
end;
"@
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($IssPath, $newContent, $utf8NoBom)
        Write-OK "DubbingToolkit_setup.iss creato in $ManifestDir"
        return "[OK] DubbingToolkit_setup.iss creato con FillAppFolders ($count cartelle)"
    }

    $content = [System.IO.File]::ReadAllText($IssPath)
    $beginMarker = "// ##CLEANUP_BEGIN##"
    $endMarker   = "// ##CLEANUP_END##"

    if ($content.IndexOf($beginMarker) -lt 0 -or $content.IndexOf($endMarker) -lt 0) {
        $snippetPath = Join-Path $ManifestDir "CleanAppFolders_snippet.txt"
        $addLines    = $folders -join "`r`n"
        $snippet = @"
procedure FillAppFolders(AppFolders: TStringList);
begin
// ##CLEANUP_BEGIN##
$addLines
// ##CLEANUP_END##
end;
"@
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($snippetPath, $snippet, $utf8NoBom)
        Write-Warn "Marcatori non trovati nel .iss - snippet salvato in CleanAppFolders_snippet.txt"
        return "[!] Marcatori non trovati - snippet salvato in CleanAppFolders_snippet.txt"
    }

    $addLines  = "`r`n" + ($folders -join "`r`n") + "`r`n"
    $pattern   = "(?s)($([regex]::Escape($beginMarker))).*?($([regex]::Escape($endMarker)))"
    $replaced  = [regex]::Replace($content, $pattern, "`$1$addLines`$2")

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($IssPath, $replaced, $utf8NoBom)
    Write-OK "FillAppFolders aggiornata nel .iss ($count cartelle)"
    return "[OK] FillAppFolders aggiornata nel .iss ($count cartelle)"
}

# ==============================================================================
# 5. MAIN EXECUTION
# ==============================================================================

Write-Header "build_manifest.ps1 - Classificazione payload DubbingToolkit"
Write-Step "Payload : $PayloadDir"
Write-Step "Manifest: $ManifestPath"

$finalEntries = Invoke-ManifestBuilder

Write-Header "Salvataggio manifest"
Save-Manifest -Entries $finalEntries
$issResult    = Build-IssPayload -Entries $finalEntries
Write-OK "payload_sections.iss generato ($($issResult.FilesCount) entries [Files], $($issResult.DirsCount) entries [Dirs], $($issResult.UninstallCount) entries [UninstallDelete])"
$cleanupResult = Update-CleanupInIss -Entries $finalEntries

$sep = "-" * 62
$systemEntries = @($finalEntries | Where-Object { $_["type"] -eq "system" } | Sort-Object { $_["path"] })
$userEntries   = @($finalEntries | Where-Object { $_["type"] -eq "user" }   | Sort-Object { $_["path"] })

Write-Host ""
Write-Host $sep -ForegroundColor Cyan
Write-Host "  Riepilogo classificazioni" -ForegroundColor Cyan
Write-Host $sep -ForegroundColor Cyan
Write-Host ""
Write-Host "  SYSTEM ($($systemEntries.Count) voci):" -ForegroundColor White
foreach ($e in $systemEntries) { Write-Host "   - $($e["path"])" -ForegroundColor Gray }
Write-Host ""
Write-Host "  USER ($($userEntries.Count) voci):" -ForegroundColor White
foreach ($e in $userEntries)   { Write-Host "   - $($e["path"])" -ForegroundColor Gray }
Write-Host ""
Write-Host $sep -ForegroundColor Cyan
Write-Host ""
Write-Host "  Completato. Voci totali nel manifest: $($finalEntries.Count)" -ForegroundColor Cyan
Write-Host "  $cleanupResult" -ForegroundColor Cyan
Write-Host ""
