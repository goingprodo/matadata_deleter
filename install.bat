@echo off
chcp 65001 > nul
echo == Stable Diffusion Installation Script ==

REM Create virtual environment using Python 3.10
echo 1. Creating virtual environment with Python 3.10...
py -3.10 -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment! Please check if Python 3.10 is installed.
    pause
    exit /b
)

REM Install other required packages
echo 2. Installing required packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements.txt! There might be version conflicts with torch.
    pause
)

echo.
echo == Installation Complete! ==
pause