@echo off
setlocal
cd /d "%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "data_tools\business_data_studio.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "data_tools\business_data_studio.py"
    exit /b 0
)

echo Uygulama baslatilamadi. Once KURULUM.bat dosyasini calistirin.
pause
