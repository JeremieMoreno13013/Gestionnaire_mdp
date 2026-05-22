@echo off
setlocal
cd /d "%~dp0\.."

py scripts\generer_logo_ico.py
if errorlevel 1 exit /b 1

py -m pip install -q "flet[all]>=0.85.0" pyinstaller
if errorlevel 1 exit /b 1

flet pack main.py ^
  -n GestionnaireMotsDePasse ^
  --icon assets\logo.ico ^
  --add-data "assets:assets" ^
  --product-name "Gestionnaire de mots de passe" ^
  --file-description "Gestionnaire de mots de passe" ^
  --company-name "Gestionnaire de mots de passe" ^
  -y
