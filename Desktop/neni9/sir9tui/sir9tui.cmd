@echo off
REM sir9tui launcher for Windows — Built by Nenifix
REM Portable: works from any folder. Uses python3 if available, else python.
cd /d "%~dp0"
where python3 >nul 2>nul
if %errorlevel%==0 (
    python3 -m sir9tui.main
) else (
    python -m sir9tui.main
)
if errorlevel 1 (
    echo.
    echo sir9tui needs Python 3.11+ with: pip install textual rich
    pause
)
