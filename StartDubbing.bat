@echo off
cd /d "%~dp0"

REM Set the ffmpeg folder as a relative variable
set "FFMPEG_PATH=%~dp0Tools\ffmpeg-7.1.1-full_build\bin"

REM Temporarily add ffmpeg to the PATH
set "PATH=%FFMPEG_PATH%;%PATH%"

REM --------------------------------------------------
REM Determine which PowerShell to use
REM --------------------------------------------------
set "PS_CMD="

REM Check if Windows PowerShell 5.1 exists
where powershell.exe >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PS_CMD=powershell.exe"
    set "PS_VERSION_LABEL=Windows PowerShell 5.1"
) else (
    REM Check if PowerShell 7 (pwsh.exe) exists
    where pwsh.exe >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PS_CMD=pwsh.exe"
        set "PS_VERSION_LABEL=PowerShell 7"
    )
)

REM Exit if no PowerShell found
if "%PS_CMD%"=="" (
    echo [ERROR] No PowerShell found. Please install either Windows PowerShell 5.1 or PowerShell 7.
    pause
    exit /b 1
)

REM --------------------------------------------------
REM Launch the script
REM --------------------------------------------------
echo [INFO] Launching %PS_VERSION_LABEL%...
start "Dubbing Project" %PS_CMD% -NoExit -ExecutionPolicy Bypass -File "%~dp0Scripts\Launcher.ps1"
