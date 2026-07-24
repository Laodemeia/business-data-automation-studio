@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

echo Gerekli Python paketleri kuruluyor...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Kurulum tamamlanamadi. Python 3 kurulu oldugundan emin olun.
    pause
    exit /b 1
)

echo.
echo Kurulum tamamlandi. BASLAT.bat dosyasini acabilirsiniz.
pause
