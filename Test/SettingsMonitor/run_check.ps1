# =========================================================
# run_check.ps1 - Avvio script Python SettingsMonitor
# =========================================================

# Vai nella cartella del progetto
cd 'D:\RecordingStudio\DubbingToolkit'

# Percorso dello script Python
$pythonScript = '.\Test\SettingsMonitor\check_settings_changes.py'

# Controllo se il file esiste
if (Test-Path $pythonScript) {
    Write-Host "File trovato: $pythonScript" -ForegroundColor Green

    # Esegui lo script Python direttamente con il Python del VENV
    try {
        & '.\venv\Scripts\python.exe' $pythonScript
    } catch {
        Write-Host "ERRORE nello script Python:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host "ATTENZIONE: il file non esiste: $pythonScript" -ForegroundColor Yellow
}

# Mantieni la finestra aperta
Read-Host -Prompt 'Premi invio per uscire'
