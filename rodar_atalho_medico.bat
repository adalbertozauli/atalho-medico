@echo off
setlocal

set "APP_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\zauli\anaconda3\python.exe"

if not exist "%PYTHON_EXE%" (
  echo Python do Anaconda nao encontrado em:
  echo %PYTHON_EXE%
  echo.
  echo Execute manualmente:
  echo python -m pip install -r requirements.txt
  echo python main.py
  pause
  exit /b 1
)

cd /d "%APP_DIR%"
"%PYTHON_EXE%" main.py

if errorlevel 1 (
  echo.
  echo O aplicativo foi encerrado com erro.
  pause
)
