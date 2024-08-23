import subprocess
import sys


def check_flutter_extension_installed():
    try:
        # Define file paths for output and error logs
        output_file = 'vscode_extensions_output.txt'
        error_file = 'vscode_extensions_error.txt'

        # PowerShell command to list installed extensions
        ps_command = (
            'Start-Process powershell -ArgumentList "code --list-extensions" '
            '-NoNewWindow -Wait -RedirectStandardOutput ' + output_file + ' -RedirectStandardError ' + error_file
        )

        # Run the PowerShell command
        subprocess.run(['powershell', '-NoProfile', '-Command', ps_command], shell=True, check=True)

        # Read output from the files with UTF-8 encoding
        with open(output_file, 'r', encoding='utf-8') as f:
            output = f.read()
        with open(error_file, 'r', encoding='utf-8') as f:
            error = f.read()

        # Define the Flutter extension ID
        flutter_extension_id = 'dart-code.flutter'

        # Check if the Flutter extension ID is in the list of installed extensions
        if flutter_extension_id in output:
            print("Flutter extension is installed.")
            print(f"Output:\n{output}")
            print(f"Error:\n{error}")
            return True
        else:
            print("Flutter extension is not installed.")
            print(f"Output:\n{output}")
            print(f"Error:\n{error}")
            return False

    except Exception as e:
        print(f"Error checking Flutter extension installation: {e}")
        return False
    
def main():
    return check_flutter_extension_installed()
    