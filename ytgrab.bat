@echo off
title ytgrab - YouTube to MP3
color 0A

echo ==================================================
echo              ytgrab - YouTube to MP3
echo        Metadata-Preserving Archival Tool
echo ==================================================
echo.

:input
set /p URL="Paste YouTube URL: "

if "%URL%"=="" (
    echo [ERROR] No URL provided. Try again.
    echo.
    goto input
)

echo.
echo Select audio quality:
echo   [1] 128 kbps (smaller file)
echo   [2] 192 kbps (default)
echo   [3] 256 kbps
echo   [4] 320 kbps (best quality)
echo.
set /p QUALITY_CHOICE="Choice [1-4, default=2]: "

if "%QUALITY_CHOICE%"=="1" set QUALITY=128
if "%QUALITY_CHOICE%"=="3" set QUALITY=256
if "%QUALITY_CHOICE%"=="4" set QUALITY=320
if not defined QUALITY set QUALITY=192

echo.
echo [INFO] Downloading at %QUALITY% kbps...
echo.

python "%~dp0ytgrab.py" "%URL%" -q %QUALITY% -o "%~dp0downloads"

echo.
echo ==================================================
echo Press any key to download another, or close window
echo ==================================================
pause >nul
cls
goto input
