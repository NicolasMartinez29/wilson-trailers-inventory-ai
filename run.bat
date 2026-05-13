@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   WILSON TRAILERS - INVENTORY AI
echo ============================================
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde python.org
    pause
    exit /b 1
)

REM Create venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [2/4] Instalando dependencias...
pip install -q --disable-pip-version-check -r requirements.txt

REM Seed only if DB missing
if not exist "wilson_inventory.db" (
    echo [3/4] Cargando datos de ejemplo...
    python -m backend.seed
) else (
    echo [3/4] Base de datos detectada - se reutiliza
)

echo [4/4] Arrancando servidor...
echo.
echo  =====================================================
echo   Abre en el navegador: http://localhost:8000
echo  =====================================================
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

endlocal
