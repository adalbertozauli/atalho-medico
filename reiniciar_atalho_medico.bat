@echo off
setlocal

set "APP_DIR=%~dp0"
set "PYTHONW_EXE=C:\Users\zauli\anaconda3\pythonw.exe"

taskkill /F /FI "WINDOWTITLE eq Atalho Médico" >nul 2>nul
taskkill /F /IM pythonw.exe >nul 2>nul

cd /d "%APP_DIR%"
start "" "%PYTHONW_EXE%" "%APP_DIR%main.py"
