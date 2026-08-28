@echo off
title Edge AI Biometric Attendance System - Production Launcher
cls
echo ======================================================================
echo    EDGE AI BIOMETRIC ATTENDANCE SYSTEM - SYSTEM LAUNCHER
echo ======================================================================
echo.
echo Select an option to run:
echo [1] Start Web Management Portal (React / Vite)
echo [2] Start Desktop Edge AI Biometric System (Python CustomTkinter)
echo [3] Start Both Web Management Portal and Edge System concurrently
echo [4] Exit
echo.
set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto desktop
if "%choice%"=="3" goto both
if "%choice%"=="4" goto end

:web
echo.
echo Starting Web Management Portal on http://localhost:5173 ...
cd web
npm run dev
goto end

:desktop
echo.
echo Starting Desktop Edge AI Biometric System...
python main.py
goto end

:both
echo.
echo Launching Web Portal in background window...
start "Web Portal" cmd /k "cd web && npm run dev"
echo Launching Desktop Edge AI Application...
python main.py
goto end

:end
pause
