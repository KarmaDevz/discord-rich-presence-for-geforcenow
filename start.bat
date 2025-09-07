@echo off
echo Iniciando Rich Presence desde el entorno virtual...

REM Cambia a la carpeta del script
cd /d "%~dp0"

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar el script con el Python del venv
python src\geforce.py

pause
