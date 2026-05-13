@echo off
cd /d "%~dp0"
if exist "wilson_inventory.db" del /q "wilson_inventory.db"
call .venv\Scripts\activate.bat
python -m backend.seed
echo Base de datos reiniciada con datos frescos.
pause
