import os
import subprocess
import urllib.request
import zipfile
import time
import sys

# Constants
PROGRAM_NAME = 'Flutter SDK'
PROGRAM_DOWNLOAD_URL = 'https://storage.googleapis.com/download.flutter_sdk/2024-08/flutter_windows_3.13.0-stable.zip'
PROGRAM_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'Flutter')
PROGRAM_COMPRESSED_FILE_NAME = 'flutter.zip'
OUTPUT_FILE = 'flutter-sdk-output.txt'
ERROR_FILE = 'flutter-sdk-error.txt'

def check_program_with_cli():
    try:
        # Open a new PowerShell window and run the 'flutter --version' command
        result = subprocess.run(['powershell', '-NoProfile', '-Command', 
                                f'Start-Process powershell -ArgumentList "flutter --version" -NoNewWindow -Wait -RedirectStandardOutput {OUTPUT_FILE} -RedirectStandardError {ERROR_FILE}'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read output from the files
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            output = f.read()
        with open(ERROR_FILE, 'r', encoding='utf-8') as f:
            error = f.read()

        # Check if the 'flutter' command is recognized
        print(f"Output:\n{output}")
        print(f"Error:\n{error}")

        return result.returncode == 0 and 'Flutter' in output
    except Exception as e:
        print(f"Error checking Flutter installation: {e}")
        return False

def download_file():
    print("Downloading Flutter SDK...")
    urllib.request.urlretrieve(PROGRAM_DOWNLOAD_URL, PROGRAM_COMPRESSED_FILE_NAME)

def install_compressed_program():
    print("Extracting Flutter SDK...")
    with zipfile.ZipFile(PROGRAM_COMPRESSED_FILE_NAME, 'r') as zip_ref:
        zip_ref.extractall(PROGRAM_PATH)

    print("Installing Flutter SDK...")
    flutter_bin_path = os.path.join(PROGRAM_PATH, 'flutter', 'bin')
    add_to_path(flutter_bin_path)
    
    # Give some time for the environment variable to be recognized
    time.sleep(5)

def add_to_path(flutter_bin_path):
    # Add Flutter SDK to PATH using PowerShell
    path_env = os.environ.get('PATH', '')
    if flutter_bin_path not in path_env:
        new_path = path_env + os.pathsep + flutter_bin_path
        print(f"Adding Flutter SDK to PATH: {flutter_bin_path}")

        # PowerShell command to update the PATH environment variable permanently
        ps_command = f"$env:PATH += '{flutter_bin_path}'; [System.Environment]::SetEnvironmentVariable('PATH', $env:PATH, [System.EnvironmentVariableTarget]::User)"
        subprocess.run(['powershell', '-Command', ps_command], shell=True, check=True)

def main():
    if not check_program_with_cli():
        print("Flutter SDK not found.")
        download_file()
        install_compressed_program()
        
        # Recheck if Flutter is now available
        if check_program_with_cli():
            print("Flutter SDK installed successfully and is accessible.")
            return True
        else:
            print("Failed to install or access Flutter SDK.")
            return False
    else:
        print("Flutter SDK is already installed.")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
