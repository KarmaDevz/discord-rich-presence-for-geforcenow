@echo off
REM === build.bat ===
REM Activa el entorno virtual
call .venv\Scripts\activate

REM Limpia compilaciones anteriores
rmdir /s /q build
rmdir /s /q dist
del /q geforce_presence.spec

REM Ejecuta PyInstaller
pyinstaller ^
  --onedir ^
  --noconsole ^
  --noconfirm ^
  --name geforce_presence ^
  --hidden-import=pystray ^
  --hidden-import=pystray._win32 ^
  --hidden-import=browser_cookie3 ^
  --hidden-import=win32gui ^
  --hidden-import=win32process ^
  --hidden-import=pypresence ^
  --hidden-import=dotenv ^
  --add-data "config;config" ^
  --add-data "assets;assets" ^
  --add-data "logs;logs" ^
  --add-data "tools;tools" ^
  --add-data "lang;lang" ^
  --icon=assets/geforce.ico ^
  --additional-hooks-dir=pyinstaller-hooks ^
  src/geforce.py

pause
