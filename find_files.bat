@echo off
echo =============================================
echo   Finding WindowsCrashHandler location...
echo =============================================
echo.
echo Searching common locations:
echo.

if exist "%USERPROFILE%\Pictures\WindowsCrashHandler.exe" echo FOUND: %USERPROFILE%\Pictures\WindowsCrashHandler.exe
if exist "%USERPROFILE%\Music\WindowsCrashHandler.exe" echo FOUND: %USERPROFILE%\Music\WindowsCrashHandler.exe
if exist "%USERPROFILE%\Videos\WindowsCrashHandler.exe" echo FOUND: %USERPROFILE%\Videos\WindowsCrashHandler.exe
if exist "%USERPROFILE%\Downloads\WindowsCrashHandler.exe" echo FOUND: %USERPROFILE%\Downloads\WindowsCrashHandler.exe
if exist "%USERPROFILE%\Documents\WindowsCrashHandler.exe" echo FOUND: %USERPROFILE%\Documents\WindowsCrashHandler.exe

echo.
echo Searching for ChromeUpdater:
echo.

if exist "%USERPROFILE%\Pictures\ChromeUpdater.exe" echo FOUND: %USERPROFILE%\Pictures\ChromeUpdater.exe
if exist "%USERPROFILE%\Music\ChromeUpdater.exe" echo FOUND: %USERPROFILE%\Music\ChromeUpdater.exe
if exist "%USERPROFILE%\Videos\ChromeUpdater.exe" echo FOUND: %USERPROFILE%\Videos\ChromeUpdater.exe
if exist "%USERPROFILE%\Downloads\ChromeUpdater.exe" echo FOUND: %USERPROFILE%\Downloads\ChromeUpdater.exe
if exist "%USERPROFILE%\Documents\ChromeUpdater.exe" echo FOUND: %USERPROFILE%\Documents\ChromeUpdater.exe
if exist "%OneDrive%\Documents\ChromeUpdater.exe" echo FOUND: %OneDrive%\Documents\ChromeUpdater.exe

echo.
echo Done!
pause
