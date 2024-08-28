import winreg
import wmi

#######################################################################################################################
# Application functions (WMI)
#######################################################################################################################
def find_installed_apps_by_wmi(app_name):
    """Find installed applications and their install locations using WMI."""
    # Initialize the WMI client
    c = wmi.WMI()

    # Initialize a dictionary to hold results
    apps_info = {}

    # Query for installed applications that match the specified name
    query = f"SELECT * FROM Win32_Product WHERE Name LIKE '%{app_name}%'"
    
    for product in c.query(query):
        display_name = product.Name
        install_location = product.InstallLocation if product.InstallLocation else 'N/A'
        apps_info[display_name] = install_location

    return apps_info

def find_installed_apps_by_registry(app_name):
    """Find installed applications and their install locations using the Windows Registry."""
    # Registry paths to search
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Wow6432Node"
    ]
    
    # Initialize a dictionary to hold results
    apps_info = {}

    # Function to search a specific registry path
    def search_registry(path):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            display_name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                            if app_name.lower() in display_name.lower():
                                install_location = winreg.QueryValueEx(subkey, 'InstallLocation')[0] if winreg.QueryValueEx(subkey, 'InstallLocation')[0] else "N/A"
                                apps_info[display_name] = install_location
                        except FileNotFoundError:
                            pass
        except FileNotFoundError:
            pass

    # Search both registry paths
    for registry_path in registry_paths:
        search_registry(registry_path)

    return apps_info

import glob
import os

def find_executable_on_path(executable_path,executable_name,executable_formats = ['exe','msi']):
    found = []
    for ext in executable_formats:
        search_path = os.path.join(executable_path,f"{executable_name}*.{ext}")
        if (result := glob.glob(search_path)):
            found.extend(result)
        
    if len(found) == 0:
        return None
    return found

import subprocess

def find_installed_apps_by_getpackage(app_name:str):
    """Run a PowerShell command and return its output, handling both stdout and stderr."""
    try:
        process = subprocess.run(
            ["powershell", "-Command", f'Get-Package | Where-Object {{$_.Name -like "*{app_name}*"}} | Select-Object Name, Version, Source | Format-Table -HideTableHeaders'],
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8',  # Ensure correct encoding
            check=True  # This raises a CalledProcessError if the command fails
        )

        apps_info = {}
        
        for line in process.stdout.splitlines():
            # Skip empty lines
            print(line)
            if line:
                # Split the line into columns
                columns = line.split()
                print(columns)
                # Extract the application name,verson and source
                app_name = columns[0]
                app_version = columns[1]
                app_source = columns[2] if len(columns) > 2 else "N/A"
                apps_info[app_name] = {
                    "version": app_version,
                    "source": app_source
                }
                
                
                
        return apps_info
    except subprocess.CalledProcessError as e:
        # Handle the error by capturing the stderr output
        error_message = e.stderr.strip()
        print(f"Error executing command: {error_message}")
        return None
        

if __name__ == "__main__":
    app_name = "Git"
    print(f"Searching for installed applications with the name '{app_name}'...\n")
 
    # Find installed applications using Get-Package
    print("Using Get-Package:")
    apps_info_getpackage = find_installed_apps_by_getpackage(app_name)
    for app, version in apps_info_getpackage.items():
        print(f"Application: {app}")
        print(f"Version: {version}")
        print()
    input("Press Enter to continue...")
