@echo off
echo =============================================
echo   PopupClient .EXE Builder
echo =============================================
echo.
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b
)
echo [1/3] Installing dependencies...
py -m pip install pyinstaller websockets pystray pillow --quiet
echo [2/3] Building WindowsCrashHandler.exe...
py -m PyInstaller --onefile --windowed --noconsole --icon=app.ico --name "WindowsCrashHandler" ws_client.py
echo [3/3] Done!
echo.
echo Your .exe is in the "dist" folder: dist\WindowsCrashHandler.exe
echo.
pause
