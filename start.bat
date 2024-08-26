@echo off
setlocal

:: Set environment variables
set MY_VARIABLE1=Value1
set MY_VARIABLE2=Value2

:: Find Python executable using 'where' command and set it
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHON_EXECUTABLE=%%i"
    goto :found
)

:: If no Python executable was found, exit with an error
echo Python executable not found. Please ensure Python is installed and available in the PATH.
exit /b 1

:found
:: Get the directory where the batch script is located
set "SCRIPT_DIR=%~dp0"

:: Define the relative path to your Python script
set "RELATIVE_PYTHON_SCRIPT_PATH=scrape.py"

:: Combine the directory and relative path to get the full path to the Python script
set "PYTHON_SCRIPT_PATH=%SCRIPT_DIR%%RELATIVE_PYTHON_SCRIPT_PATH%"

:: Construct the command to run the Python script
set "COMMAND=%PYTHON_EXECUTABLE% \"%PYTHON_SCRIPT_PATH%\""

:: Run the Python script as an administrator and keep the window open
echo Running Python script as administrator...
powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/k %COMMAND%' -Verb RunAs"

endlocal