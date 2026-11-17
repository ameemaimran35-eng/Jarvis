@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   J.A.R.V.I.S Launcher (Module 4)
echo ========================================
echo.

:: 1. Check if the Python virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at:
    echo   %~dp0venv\Scripts\python.exe
    echo.
    echo Please set up your virtual environment first:
    echo   1. python -m venv venv
    echo   2. venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: 2. Check if .env configuration file exists
if not exist ".env" (
    echo [WARNING] .env file not found.
    echo Please copy .env.example to .env and configure your Gemini API key:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

:: 3. Launch JARVIS with any provided arguments (e.g., --text)
"venv\Scripts\python.exe" main.py %*
set EXIT_CODE=%ERRORLEVEL%

:: 4. If JARVIS terminated with an error, keep the console window open
if %EXIT_CODE% neq 0 (
    echo.
    echo [NOTICE] JARVIS stopped with exit code %EXIT_CODE%.
    pause
)

endlocal
