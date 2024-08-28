@echo off
setlocal

:: Create a virtual environment
python -m venv .scraper-venv

:: Activate the virtual environment
call .scraper-venv\Scripts\activate

:: Set environment variables
set PYPPETEER_CHROMIUM_REVISION='1263111'

:: Get the directory where the batch script is located
set "SCRIPT_DIR=%~dp0"

:: Install Python dependencies
python install -r "%SCRIPT_DIR%requirements.txt"

:: Python venv executable, using relative path
set "PYTHON_EXECUTABLE=%SCRIPT_DIR%.scraper-venv\Scripts\python.exe"

:: Define the relative path to your Python script
set "RELATIVE_PYTHON_SCRIPT_PATH=scrape.py"

:: Combine the directory and relative path to get the full path to the Python script
set "PYTHON_SCRIPT_PATH=%SCRIPT_DIR%%RELATIVE_PYTHON_SCRIPT_PATH%"

:: Check if there are additional arguments provided
set "ARGS=%*"

:: Construct the command to run the Python script with additional arguments
set "COMMAND=%PYTHON_EXECUTABLE% \"%PYTHON_SCRIPT_PATH%\" %ARGS%"

:: Run the Python script as an administrator and keep the window open
echo Running Python script as administrator...
powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/k %COMMAND%' -Verb RunAs"

endlocal
