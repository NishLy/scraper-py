import subprocess

from typing import Dict

def run_powershell_with_text_output(command: str) -> Dict[str, str]:
    """Run a PowerShell command and return its output, handling both stdout and stderr."""
    try:
        process = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8',  # Ensure correct encoding
            check=True  # This raises a CalledProcessError if the command fails
        )
        return {
            "stdout": process.stdout.strip(),
            "stderr": None
        }
    except subprocess.CalledProcessError as e:
        # Handle the error by capturing the stderr output
        error_message = e.stderr.strip()
        print(f"Error executing command: {error_message}")
        return {
            "stdout": None,
            "stderr": error_message
        }
        
