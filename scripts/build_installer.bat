@echo off
setlocal
cd /d "%~dp0\.."

call scripts\build_windows.bat
if errorlevel 1 exit /b 1

if not exist "dist\GestionnaireMotsDePasse.exe" (
    echo dist\GestionnaireMotsDePasse.exe introuvable.
    exit /b 1
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo Inno Setup 6 requis : https://jrsoftware.org/isdl.php
    exit /b 1
)

"%ISCC%" "installer\GestionnaireMotsDePasse.iss"
if errorlevel 1 exit /b 1
