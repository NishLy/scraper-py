import subprocess

def run_powershell_with_text_output(command: str) -> str:
    """Run a PowerShell command and return its output."""
    process = subprocess.run(["powershell", "-Command", command],
                             capture_output=True, text=True, shell=True,encoding='utf-8')
    return process.stdout.strip()