@echo off
:: Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

:: Run the Python script from its original directory
cd /d "%SCRIPT_DIR%"
python chat_bot.py