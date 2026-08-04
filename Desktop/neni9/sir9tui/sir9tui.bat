@echo off
title sir9tui — AI STEM Tutor by Nenifix
color 0B
cls
echo.
echo   ╔═══════════════════════════════════════════════╗
echo   ║   sir9tui — AI STEM Tutor by Nenifix          ║
echo   ║   Press 'q' to quit                           ║
echo   ╚═══════════════════════════════════════════════╝
echo.
cd /d "%~dp0"
where python3 >nul 2>nul
if %errorlevel%==0 (
    python3 -m sir9tui.main
) else (
    python -m sir9tui.main
)
echo.
echo sir9tui closed.
pause
