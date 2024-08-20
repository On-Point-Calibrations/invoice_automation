:: usage: create a *shortcut* to this file somewhere easliy accessible. Don't relocate this file!

@echo off

REM Define the Python file name you want to run
set "pythonFile=main.py"

REM Check if the file exists in the current directory
if exist "%~dp0%pythonFile%" (
    REM Launch the Python script using the default Python interpreter
    python "%~dp0%pythonFile%"
) else (
    echo File "%pythonFile%" not found in the current directory.
)

REM Wait for user input before closing
echo.
echo Press any key to close this window...
pause >nul
