import asyncio.runners
import importlib
import subprocess
import sys
import os
import time
import glob
import platform
import jsongi
import traceback
import threading
import pythoncom

#######################################################################################################################
# Arg vars
NO_CONFIRM = False
SKIP_CHECKED = False
SKIP_HOST_CHECK = False
#######################################################################################################################



#######################################################################################################################
# Bootstrap pip
#######################################################################################################################

pip_ready_to_use = subprocess.run([sys.executable, '-m', 'pip', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0

if not pip_ready_to_use:
    # Install pip
    try:
        subprocess.run([sys.executable, '-m', 'ensurepip', '--default-pip'], check=True)
        print("Pip has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pip: {e}")
        sys.exit(1)

#######################################################################################################################
# JSON utils function
#######################################################################################################################

def read_json(file_path):
    """Read JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
    
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

def write_json(data, base_filename):
    """Write JSON data to a file with a timestamp in the filename."""
    if not isinstance(data, dict):
        print("Data must be a dictionary.")
        return
    
    data['timestamp'] = time.time()
    filename = f"{base_filename}"
    
    with open(filename, 'w') as file:
        try:
            json.dump(data, file, indent=4)
        except (TypeError, ValueError) as e:
            print(f"Error writing JSON: {e}")
            

#######################################################################################################################
# CONSTANT VARS
PATH_TO_JSON_LOG = os.curdir + '/log.json'
PATH_INSTRUCTIONS = os.curdir + '/instructions'
KEYBOARD_MOUSE_TEST_SITE = 'https://en.kFey-test.ru/'
REQUIRED_MODULES = ['setuptools','pyppeteer','wmi','pywintypes','pytz','ntplib','platform','psutil','GPUtil','pyperclip','colorama','tabulate']
#######################################################################################################################

#######################################################################################################################
# Loaded variable
#######################################################################################################################


JSON_LOG = read_json(PATH_TO_JSON_LOG) if os.path.exists(PATH_TO_JSON_LOG) else {
    "Description": "This is a log file for the host information and the application status.",
    "HOST":{
        "PC-NAME": os.environ['COMPUTERNAME'],
        "OS": platform.system(),
        "OS-VERSION": platform.version(),
        "OS-RELEASE": platform.release(),
        "OS-ARCHITECTURE": platform.architecture(),
    },
    "HOST-SPECS":{},
    "APPLICATION-STATUS": {}
}

instructions = []

if os.path.exists(PATH_INSTRUCTIONS):
    for file in os.listdir(PATH_INSTRUCTIONS):
        base, ext = os.path.splitext(file)
        if ext.lower() == '.py':
            instructions.append(base.lower())
else:
    # close the app
    print(f"Instructions folder not found. Please create a folder named 'instructions' in the same directory as this script.")
    sys.exit(1)

#######################################################################################################################
# Check module function
#######################################################################################################################
def check_module_installed(module_name):
    """Check if a module is installed by trying to import it."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_module(module_name):
    """Install a module using pip."""
    try:
        # Install the module using pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module_name])
        print(f"Module '{module_name}' has been successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install module '{module_name}': {e}")
        sys.exit(1)
        
def check_required_modules():
    for module_name in REQUIRED_MODULES:
        if not check_module_installed(module_name):
            print(f"Module '{module_name}' is not installed. Installing...")
            install_module(module_name)
    print("All required modules are installed.")
 
check_required_modules()


#######################################################################################################################
#Late module import
#######################################################################################################################

import argparse
import asyncio
import os
import re
import tkinter as tk
from tkinter import messagebox
import wmi
from pyppeteer import launch
import ntplib
from datetime import datetime
import pytz
import platform
from colorama import Fore, Style, init, Back

init(autoreset=True)

#######################################################################################################################
# NTP Time functions
#######################################################################################################################
def get_ntp_time():
    """Fetch the current time from an NTP server."""
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    return response.tx_time

def set_system_time(new_time):
    """Set the system time (requires administrative privileges)."""
    formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
    
    if platform.system() == "Windows":
        # Windows command to set the system time
        date_cmd = new_time.strftime('Set-Date -Date "%m-%d-%Y %H:%M"')
        result = subprocess.run(["powershell", "-Command", date_cmd])
        if result.returncode != 0:
            raise OSError("Failed to set system time")
        else:
            print(f"System time set to {formatted_time}")
            return True
    elif platform.system() == "Linux":
        # Linux command to set the system time
        try:
            subprocess.run(['sudo', 'timedatectl', 'set-time', formatted_time], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error setting system time: {e}")
    else:
        raise OSError("Unsupported operating system")

def set_time():
    # Fetch current time from NTP server
    ntp_time = get_ntp_time()

    # Convert to UTC+7
    utc = pytz.utc
    local_tz = pytz.timezone('Asia/Bangkok')  # UTC+7 timezone
    utc_time = datetime.utcfromtimestamp(ntp_time).replace(tzinfo=utc)
    local_time = utc_time.astimezone(local_tz)

    # Print the local time for verification
    print(f"Current local time (UTC+7): {local_time.strftime('%Y-%m-%d %H:%M:%S')}")


    # Set the system time
    set_system_time(local_time)
    # Set the system time
 
 
#######################################################################################################################
# Application functions (WMI)
#######################################################################################################################
def check_application_installed(app_name):
    """Find installed applications and their install locations using WMI."""
    # Initialize the WMI client
    pythoncom.CoInitialize()
    c = wmi.WMI()

    # Initialize a dictionary to hold results
    apps_info = {}

    # Query for installed applications that match the specified name
    query = f"SELECT * FROM Win32_Product WHERE Name LIKE '%{app_name}%'"
    
    for product in c.query(query):
        display_name = product.Name
        install_location = product.InstallLocation if product.InstallLocation else 'N/A'
        apps_info[display_name] = install_location

    pythoncom.CoUninitialize()
    return apps_info

import winreg
import json

def find_installed_apps_in_registry(app_name):
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
 
 
def get_yes_or_no(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")
 
 
import glob
def open_application(executable_path,app_name):
    search_pattern_exe = os.path.join(executable_path, f'{app_name}*.exe')
    search_pattern_msi = os.path.join(executable_path, f'{app_name}*.msi')
    exe_files = glob.glob(search_pattern_exe)
    msi_files = glob.glob(search_pattern_msi)
    
    if not exe_files and not msi_files: 
        print(Fore.RED + f"No executable (MSI,EXE) files found for {app_name}. at {executable_path}")
        print(Back.MAGENTA + Fore.WHITE + "Please confirm the lines below (Cannot skiped in --dangerously-say-yes)")
        if get_yes_or_no("Open the installation path? (y,n)"):
            subprocess.run(
            ['powershell', '-NoProfile', '-Command',f'explorer {executable_path}'], shell=True,check=True
        )
        get_yes_or_no("Is in the installation path have executable file and it run successfuly ? (y,n)")
        return None
    
    for file in exe_files + msi_files:
        if file and os.path.isfile(file):
            proccess = subprocess.Popen(file)
            return proccess

    return None
 
 
#######################################################################################################################
# Popup functions
#######################################################################################################################
 
def show_info_popup(message):
 
    root = tk.Tk()
 
    root.withdraw()  # Hide the root window
 
    messagebox.showinfo("Information", message)
 
    root.destroy()
 
 
def show_warning_popup(message):
 
    root = tk.Tk()
 
    root.withdraw()  # Hide the root window
 
    messagebox.showwarning("Warning", message)
 
    root.destroy()
 
 
def show_confirmation_popup(message,**kwargs):
    if kwargs.get("no_confirm",False):
        if kwargs.get("evaluate",False):
            print(Fore.WHITE + Back.CYAN + f">>> Confirmation Protocol Skiped. Return evaluation is {Fore.WHITE + Back.GREEN}True")
            return True
        else:
            print(Fore.WHITE + Back.CYAN + f">>> Confirmation Protocol Skiped. Return evaluation is {Fore.WHITE + Back.RED}False")
            return False
    
    root = tk.Tk()
    root.withdraw()  # Hide the main root window

    # Create a Toplevel window
    messagebox = tk.Toplevel()
    messagebox.title("Confirmation")
    messagebox.attributes("-topmost", True)  # Keep the message box on top

    # Set the message box size and position
    messagebox.geometry("600x150")  # Increase width, reduce height
    messagebox.resizable(False, False)

    # Create and pack the message label
    label = tk.Label(messagebox, text=message, wraplength=350, font=('Helvetica', 12))
    label.pack(pady=20, padx=20)

    # Variable to store the user's response
    response = tk.BooleanVar()

    # Define the actions for Yes and No buttons
    def on_yes():
        response.set(True)
        messagebox.destroy()

    def on_no():
        response.set(False)
        messagebox.destroy()

    # Create and pack Yes and No buttons
    button_style = {'font': ('Helvetica', 14), 'width': 10, 'height': 2}
    yes_button = tk.Button(messagebox, text="Yes", command=on_yes, **button_style)
    yes_button.pack(side=tk.LEFT, padx=30, pady=10)

    no_button = tk.Button(messagebox, text="No", command=on_no, **button_style)
    no_button.pack(side=tk.RIGHT, padx=30, pady=10)

    # Center the window on the screen
    messagebox.update_idletasks()
    width = messagebox.winfo_width()
    height = messagebox.winfo_height()
    x = (messagebox.winfo_screenwidth() // 2) - (width // 2)
    y = (messagebox.winfo_screenheight() // 2) - (height // 2)
    messagebox.geometry(f"{width}x{height}+{x}+{y}")

    # Wait for the user to close the message box
    messagebox.grab_set()  # Make the window modal
    messagebox.wait_window()

    # Return the boolean value based on the user's response
    return response.get()




#######################################################################################################################
# Mouse and Keyboard functions
#######################################################################################################################

def check_mouse():
    print("Opening mouse test website...")
    subprocess.run(['powershell', 'start', KEYBOARD_MOUSE_TEST_SITE])
    
def check_keyboard():
    print("Opening keyboard test website...")
    subprocess.run(['powershell', 'start', KEYBOARD_MOUSE_TEST_SITE])
    
    
#######################################################################################################################
# Check chrome function
#######################################################################################################################

def check_chrome():
    result = subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe"])
    print(result)
    return result

#######################################################################################################################
# Check Virtualization function
#######################################################################################################################

def check_virtualization():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    for processor in c.Win32_Processor():
        if hasattr(processor, 'VirtualizationFirmwareEnabled'):
            if processor.VirtualizationFirmwareEnabled:
                print("#"*150)
                print("This Computer CPU Virtualization is enabled")
                print("#"*150)
                pythoncom.CoUninitialize()
                return True
            else:
                print("#"*150)
                print("This Computer CPU Virtualization is not enabled")
                print("#"*150)
                pythoncom.CoUninitialize()
                return False
        else:
            print("#"*150)
            print("This Computer CPU Virtualization is not enabled")
            print("#"*150)
            pythoncom.CoUninitialize()
            return False
    pythoncom.CoUninitialize()
    return None

#######################################################################################################################
# Format Drive D: / E: function
#######################################################################################################################

def format_drive():
    if platform.system() == "Windows":
        # Windows command to format drive
        try:
            subprocess.run(['format', 'D:', '/fs:NTFS', '/v:Drive D:', '/q'], check=True)
            subprocess.run(['format', 'E:', '/fs:NTFS', '/v:Drive E:', '/q'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error formatting drive: {e}")
    else:
        raise OSError("Unsupported operating system")
    
#######################################################################################################################
# Check Visual Studio Code
#######################################################################################################################

def check_vscode_installed():
    try:
        # Define file paths for output and error logs
        output_file = 'vscode_output.txt'
        error_file = 'vscode_error.txt'

        # Run the 'code --version' command in PowerShell and redirect output to files
        subprocess.run(
            ['powershell', '-NoProfile', '-Command', 
             'Start-Process powershell -ArgumentList "code --version" -NoNewWindow -Wait -RedirectStandardOutput ' + output_file + ' -RedirectStandardError ' + error_file],
            shell=True,
            check=True
        )

        # Read output from the files with UTF-8 encoding
        with open(output_file, 'r', encoding='utf-8') as f:
            output = f.read()
        with open(error_file, 'r', encoding='utf-8') as f:
            error = f.read()

        # Check if the output contains version information
        if output.strip():  # Check if there is any non-empty output
            print("Visual Studio Code is installed.")
            print(f"Output:\n{output}")
            print(f"Error:\n{error}")
            return True
        else:
            print("Visual Studio Code is not installed or version command failed.")
            print(f"Output:\n{output}")
            print(f"Error:\n{error}")
            return False

    except Exception as e:
        print(f"Error checking Visual Studio Code installation: {e}")
        return False
    
#######################################################################################################################
#CONSTANT VALUE //Start
#######################################################################################################################

CONSTANT_CHECK = {
    "date-time": {
        "function": set_time,
       " message_success": "Date & Time has been set successfully.",
        "message_fail": "Date & Time has not been set.",
        "message_confirmation": "Do you want to set the Date & Time to UTC +7?"
    },
    "mouse": {
        "function": check_mouse,
        "message_success": "Mouse is working.",
        "message_fail": "Mouse is not working.",
        "message_confirmation": "Is the mouse working properly?"
    },
    "keyboard": {
        "function": check_keyboard,
        "message_success": "Keyboard is working.",
        "message_fail": "Keyboard is not working.",
        "message_confirmation": "Is the keyboard working properly?"
    },
    "chrome": {
        "function": check_chrome,
        "message_success": "Chrome is working.",
        "message_fail": "Chrome is not working.",
        "message_confirmation": "Is Chrome working properly?"
    },
    "virtualization": {
        "function": check_virtualization,
        "message_success": "Virtualization is enabled.",
        "message_fail": "Virtualization is not enabled.",
        "message_confirmation": "Is Virtualization enabled?"
    },
    "format-drive:e,f": {
        "function": None,
        "message_success": "Drive D: / E: is formatted.",
        "message_fail": "Drive D: / E: is not formatted.",
        "message_confirmation": "Is Drive D: / E: formatted?"
    },
    "visual-studio-code": {
        "function": check_vscode_installed,
        "message_success": "Visual Studio Code is installed.",
        "message_fail": "Visual Studio Code is not installed.",
        "message_confirmation": "Is Visual Studio Code installed?"
    }
}


#######################################################################################################################
# Application Check
#######################################################################################################################


def chose_app_to_open(app_list):
    for i,app in enumerate(app_list):
        print(f"{i}. {app}")
        
    is_in_invalid = True
    
    while is_in_invalid:
        input_num = input("Input number to chose or 'all' to open each instalation path : ")
        
        if input_num == 'all':
            for i,app in enumerate(app_list):
                open_application(app_list[app],app)
            return -1
        else:
            try:
                index = int(input_num)
                if index in range(len(app_list)):
                    is_in_invalid = False
                    key = list(app_list.keys())[index]
                    return key                
            except ValueError:
                print("Invalid index")


        
def _check_app(label_app_name,**kwargs):
    print(f"Running function check_app on thread: {threading.current_thread().name}")
    

    if label_app_name in JSON_LOG['APPLICATION-STATUS']:
        del JSON_LOG['APPLICATION-STATUS'][label_app_name]

    log_app = {
        "Name": label_app_name,
        "Status" : "NOT_INSTALLED", # NOT_INSTALLED, INSTALLED, NEWLY_INSTALLED
        "Install_Location": "N/A",
        "Description": "",
        "Check_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Check_Duration": 0,
        "Check_with" : None
    }

    start_time = time.time()
    check_with = None

    if label_app_name in CONSTANT_CHECK:
        try:
            print(Fore.CYAN + f"{label_app_name} is available in CONSTANT_CHECK. Trying to run the function...")
            evaluate = CONSTANT_CHECK[label_app_name]['function']()
            if show_confirmation_popup(CONSTANT_CHECK[label_app_name]['message_confirmation'],no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                print(Fore.YELLOW + f">>> CALLBACK-MESSAGE : {CONSTANT_CHECK[label_app_name]['message_success']}")
                log_app["Status"] = "INSTALLED"
                log_app["Description"] = CONSTANT_CHECK[label_app_name]['message_success']
            else:
                print(Fore.YELLOW +f">>> CALLBACK-MESSAGE : {CONSTANT_CHECK[label_app_name]['message_fail']}")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] = CONSTANT_CHECK[label_app_name]['message_fail']
            if evaluate and type(evaluate) == subprocess.Popen:
                evaluate.kill()
            check_with = "CONSTANT_CHECK"
        except Exception as e:
                print(Back.RED + Fore.WHITE + f"CALLBACK-MESSAGE : {CONSTANT_CHECK[label_app_name]['message_fail']}")
                print(Back.YELLOW + Fore.BLACK + "Skiping 'CONSTANT CHECK' because error occured")
                log_app['Description'] = log_app["Description"] + " - " + CONSTANT_CHECK[label_app_name]['message_fail']
        
    if not check_with and (result := check_application_installed(label_app_name.replace("-", ""))) not in [None, {}]:
        print(Fore.CYAN + f"{label_app_name} is detected in WMI. Trying to open the application...")
        if all(value == "N/A" for value in result.values()):
            print(Fore.BLACK + Back.YELLOW + f"{label_app_name} found in WMI, But WMI cannot provide instalation path. Skiping WMI or try open it manualy")
            log_app["Description"] = log_app["Description"] + " - " + f"{label_app_name} found in WMI, But WMI cannot provide instalation path."
        else:
            try:
                key = 0
                if len(result) > 1:
                    print(Fore.MAGENTA + f"Multiple installations found in WMI for '{label_app_name}'. Please select or open each istalation path" )
                    key = chose_app_to_open(result)
                else:
                    key = list(result.keys())[0]
                
                evaluate = None
                
                if key != -1:
                    evaluate = open_application(result[key],label_app_name)
                
                if show_confirmation_popup(f"Did {label_app_name} working successfully?",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Install_Location"] = result[key]
                    log_app["Description"] = f'{label_app_name} is working.'
                else:
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] = f'{label_app_name} is not working.'
                if evaluate and type(evaluate) == subprocess.Popen:
                    evaluate.terminate()
                check_with = "WMI"
            except Exception as e:
                print(Back.RED + Fore.WHITE + f"Error open {label_app_name} with WMI : {e}")
                print(Back.YELLOW + Fore.BACK + "Skiping 'WMI' because error occured")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] = log_app["Description"] + " - " + f"Error loading module: {e}"    
                            
    if not check_with and (result := find_installed_apps_in_registry(label_app_name.replace("-", ""))) not in [None, {}] :
        print(Fore.CYAN + f"{label_app_name} is detected in WMI. Trying to open the application...")
        if all(value == "N/A" for value in result.values()):
            print(Fore.BLACK + Back.YELLOW + f"{label_app_name} found in REGISTRY, But REGISTRY cannot provide instalation path. Skiping REGISTRY or try open it manualy")
            log_app["Description"] = log_app["Description"] + " - " + f"{label_app_name} found in REGISTRY, But REGISTRY cannot provide instalation path."
        else:
            try:
                key = 0
                if len(result) > 1:
                    print(Fore.MAGENTA + f"Multiple installations in REGISTRY found for '{label_app_name}'. Please select or open each istalation path" )
                    key = chose_app_to_open(result)
                else:
                    key = list(result.keys())[0]
                
                evaluate = None
                
                if key != -1:
                    evaluate = open_application(result[key],label_app_name)
                    
                if show_confirmation_popup(f"Did {label_app_name} working successfully?",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Install_Location"] = result[key]
                    log_app["Description"] = f'{label_app_name} is working.'
                else:
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] = f'{label_app_name} is not working.'
                    
                if evaluate and type(evaluate) == subprocess.Popen:
                    evaluate.terminate()
                check_with = "REGISTRY"
                
            except Exception as e:
                print(Back.RED + Fore.WHITE + f"Error open {label_app_name} with REGISTRY : " + str(e))
                print(Back.YELLOW + Fore.BLACK + "Skiping 'REGISTRY' because error occured")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] = f"Error opening {label_app_name} : " + str(e)

    if not check_with and label_app_name.lower() in instructions:
        print(Fore.CYAN + f"{label_app_name} is available in instructions. Trying to run the function...")
        try:
            # Get the module name (without .py extension)
            module_name = label_app_name.lower()

            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, PATH_INSTRUCTIONS + "/" + label_app_name.lower() + '.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'main'):
                
                evaluate = module.main()
        
                if not kwargs.get("no_confirm",False):
                    if evaluate:
                        print(Fore.YELLOW + f"{label_app_name} is working?. Executed instruction Is returning True")
                    else:
                        print(Fore.YELLOW + f"{label_app_name} is not working?. Executed instruction Is returning False")
                if show_confirmation_popup(f"Instruction has been executed, Did {label_app_name} work successfully?",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Description"] = f"{evaluate}"
                else:       
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] =  f"{evaluate}"
                check_with = "INSTRUCTION"
                
            else:
                print(Back.RED + Fore.WHITE +f"No 'main' function found in {label_app_name}.py")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] =  f"No 'main' function found in {label_app_name}.py"

        except Exception as e:
            print(Back.RED + Fore.WHITE +f"Error loading module: {e}")
            print(Back.YELLOW + Fore.BLACK + "Skiping 'INSTRUCTION' because error occured")
            log_app["Status"] = "NOT_INSTALLED"
            log_app["Description"] = log_app["Description"] + " - " +f"Error loading module: {e}"

    ## fail from all checking

    if not check_with and not kwargs.get("dangerously_say_yes",False) :
        if show_confirmation_popup(f"{label_app_name} cannot be opened or detected. Do you want to mark it as installed?"):
            print(Fore.YELLOW + f">>> {label_app_name} cannot be opened or detected. Marked as installed.")
            log_app["Status"] = "INSTALLED"
            log_app["Description"] = log_app["Description"] + " - " + f'{label_app_name} is not detected. Marked as installed'
        else:
            print(Fore.RED + f">>> {label_app_name} is not detected. Marked as not installed.")
            log_app["Status"] = "NOT_INSTALLED"
            log_app["Description"] = log_app["Description"] + " - " + f'{label_app_name} is not detected. Marked as not installed'

    else:
        if not check_with:
            print(Fore.RED + f">>> {label_app_name} is not detected. Marked as not installed.")
            log_app["Status"] = "NOT_INSTALLED"
            log_app["Description"] = log_app["Description"] + " - " + f'{label_app_name} is not detected. Marked as not installed'

    log_app["Check_Time"] = time.time() - start_time
    log_app["Check_with"] = check_with
    JSON_LOG['APPLICATION-STATUS'][label_app_name] = log_app
    write_json(JSON_LOG, PATH_TO_JSON_LOG)
    

async def _check_applications(apps, **kwargs):
    print("Main thread :", threading.current_thread().name)
    
    async def run_in_thread(label_app_name):
        from functools import partial
        loop = asyncio.get_running_loop()
        partial_func = partial(_check_app,label_app_name,**kwargs)
        result = await loop.run_in_executor(None,partial_func)
        return result
    
    print('-' * 150)
    print("Start checking each required app or tools.")
    print('-' * 150)

    checked_apps = [app for app in JSON_LOG['APPLICATION-STATUS']]
    installed_apps = None
    
    if kwargs.get('skip_installed',False):
        installed_apps = [app for app in JSON_LOG['APPLICATION-STATUS'] if JSON_LOG['APPLICATION-STATUS'][app]['Status'] == 'INSTALLED']
    
    if not kwargs.get('async',False):
        for label_app_name in apps:
            label_app_name = label_app_name.lower()
            if kwargs.get('skip_checked',False) and label_app_name in checked_apps:
                print(f"{label_app_name} has been checked before. Skipping...")
                continue
            if installed_apps and label_app_name in installed_apps:
                print(f"{label_app_name} has been marked installed before. Skipping...")
                continue
            _check_app(label_app_name,**kwargs)
        print('App cheking run syncronously, all apps checked.')
    else:
        print('App cheking run asyncronously, waiting for all tasks to complete...')
        
        apps = [label_app_name.lower() for label_app_name in apps]
        apps = [label_app_name for label_app_name in apps if kwargs.get('skip_checked',False) and label_app_name not in checked_apps] if kwargs.get('skip_checked',False) else apps
        apps = [label_app_name for label_app_name in apps if installed_apps and label_app_name not in installed_apps] if installed_apps else apps
        
        tasks = [run_in_thread(label_app_name) for label_app_name in apps]
        results = await asyncio.gather(*tasks)
            
    print('-' * 150)
    print("Cheking apps completed.")
    print('-' * 150)
        
    print("-" * 150)
    print("CHECK SUMMARY")
    print("-"*150)

    for i,app in enumerate(JSON_LOG['APPLICATION-STATUS']):
        print(f"{i}. {app} : {JSON_LOG['APPLICATION-STATUS'][app]['Status']}")
        print(f"Description : {JSON_LOG['APPLICATION-STATUS'][app]['Description']}")
        print(f"Check Duration : {JSON_LOG['APPLICATION-STATUS'][app]['Check_Time']} seconds")
        print(f"Check with : {JSON_LOG['APPLICATION-STATUS'][app]['Check_with']}")
        print("-"*150)
    


#######################################################################################################################
#MAIN FUNCTION SCRAPE
#######################################################################################################################

async def _scrape(username, password, **kwargs):
 
 
        # # Launch a new browser instance
 
        # browser = await launch(headless=False,timeout=60000)
 
        # page = await browser.newPage()
 
 
        # # Navigate to the login page
 
        # await page.goto('http://192.168.10.69/ceksoft/login.php')  # Replace with your login page URL
 
 
        # # Fill out the login form
 
        # await page.type('[name="username"]', username)  # Replace with your username input selector
 
        # await page.type('[name="password"]', password)  # Replace with your password input selector
 
 
        # # Submit the login form
 
        # await page.click('[name="login"]')  # Replace with your login button selector
 
        # await page.waitForNavigation()    # Wait for navigation to complete
 
 
        # # Now navigate to the page containing the table
 
        # # await page.goto('http://192.168.10.69/ceksoft/index.php')  # Replace with the URL of the page with the table
 
 
        # # Extract text from the label within the first cell of each row
 
        # labels = await page.evaluate('''
 
        #     () => {
 
        #         // Find the table with the specific ID
 
        #         const table = document.querySelector('#dataSoftware');
 
        #         if (!table) return [];
 
 
        #         // Get all rows in the table
 
        #         const rows = table.querySelectorAll('tr');
 
        #         const extractedTexts = [];
 
 
        #         rows.forEach(row => {
 
        #             // Find the first cell in the row
 
        #             const firstCell = row.querySelector('td');
 
        #             if (firstCell) {
 
        #                 // Find the label element within the first cell
 
        #                 const label = firstCell.querySelector('label');
 
        #                 if (label) {
 
        #                     extractedTexts.push(label.textContent.trim());
 
        #                 }
 
        #             }
 
        #         });
 
 
        #         return extractedTexts;
 
        #     }
 
        # ''')
 
 
        # Print the extracted text
        labels = ['flutter-sdk',"visual-studio-code",'flutter-extension','virtualization','python','git', 'virtual-box', 'chrome']

        print('-' * 150)
        print("Applications to check:")
        print('-' * 150)
        
        for label in labels:
            print(f"- {label}")
            
        await _check_applications(labels, **kwargs)
     
 
 
    
#######################################################################################################################
# FUNTIONS TO GET HOST INFO
#######################################################################################################################

import psutil
import platform
import GPUtil
import wmi

# Define data fetching functions (as previously discussed)
def get_cpu_info():
    w = wmi.WMI()
    cpu_list = []
    for processor in w.Win32_Processor():
        cpu_info = {
            "Name": processor.Name.strip(),
            "Cores": processor.NumberOfCores,
            "Threads": processor.ThreadCount,
            "ClockSpeed": f"{processor.MaxClockSpeed / 1500:.2f} GHz",
            "Manufacturer": processor.Manufacturer.strip(),
            "TDP": "N/A",  # TDP information is not available from WMI
            "Generation": "N/A"  # Generation information is not available from WMI
        }
        cpu_list.append(cpu_info)
    return cpu_list

def get_ram_info():
    w = wmi.WMI()
    ram_list = []
    for memory in w.Win32_PhysicalMemory():
        ram_info = {
            "Manufacturer": memory.Manufacturer.strip(),
            "Capacity (GB)": f"{int(memory.Capacity) / (1024 ** 3):.2f}",
            "Type": memory.MemoryType,
            "Speed (MHz)": f"{memory.Speed} MHz"
        }
        ram_list.append(ram_info)
    return ram_list

def get_gpus_info():
    # Initialize WMI and GPUtil
    w = wmi.WMI()
    gpus = GPUtil.getGPUs()
    
    gpu_info_list = []
    
    # Collect GPU info from WMI
    video_cards = w.Win32_VideoController()
    for card in video_cards:
        gpu_info = {
            "Name": card.Name.strip(),
            "Manufacturer": card.AdapterCompatibility.strip(),
            "VRAM (GB)": int(card.AdapterRAM) / (1024 ** 3),
            "Core Clock Speed (MHz)": "Not Available via WMI",
            "Architecture": "Integrated" if "Intel" in card.Name or "AMD" in card.Name else "Discrete"
        }
        gpu_info_list.append(gpu_info)
    
    # Collect additional GPU info from GPUtil
    for gpu in gpus:
        gpu_info = {
            "Name": gpu.name.strip(),
            "Manufacturer": gpu.vendor.strip(),
            "VRAM (GB)": gpu.memoryTotal / 1024,
            "Core Clock Speed (MHz)": gpu.clockSpeed,
            "Architecture": gpu.name.split()[0]  # Rough estimation of architecture
        }
        gpu_info_list.append(gpu_info)
    
    return gpu_info_list

def get_disk_info():
    w = wmi.WMI()
    disk_list = []
    for disk in w.Win32_DiskDrive():
        disk_info = {
            "DeviceID": disk.DeviceID.strip(),
            "Size (GB)": f"{int(disk.Size) / (1024 ** 3):.2f}",
            "Manufacturer": disk.Manufacturer.strip(),
            "InterfaceType": disk.InterfaceType
        }
        disk_list.append(disk_info)
    return disk_list

def get_network_info():
    w = wmi.WMI()
    adapters = w.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    network_list = []
    
    for adapter in adapters:
        hardware_info = []
        if adapter.Description:
            hardware_info = w.Win32_NetworkAdapter(Description=adapter.Description)
        
        if hardware_info:
            hardware_info = hardware_info[0]
            manufacturer = hardware_info.Manufacturer.strip() if hardware_info.Manufacturer else "Unknown"
        else:
            manufacturer = "Unknown"

        adapter_info = {
            "Description": adapter.Description.strip(),
            "Manufacturer": manufacturer,
            "MACAddress": adapter.MACAddress,
            "IPAddresses": adapter.IPAddress[0] if adapter.IPAddress else "No IP Address",
            "IPSubnet": adapter.IPSubnet[0] if adapter.IPSubnet else "No Subnet",
            "DefaultIPGateway": adapter.DefaultIPGateway[0] if adapter.DefaultIPGateway else "No Gateway",
            "Type": "Wi-Fi" if 'Wi-Fi' in adapter.Description or 'Wireless' in adapter.Description else "LAN"
        }
        
        network_list.append(adapter_info)
    
    return network_list

#######################################################################################################################
# MAIN FUNCTION HOST INFO
#######################################################################################################################

async def get_host_info():
    
    print("-"*50)
    print("Getting host information...")
    print("-"*50)
    # Get CPU information
    cpu_info = get_cpu_info()
    print("CPU Information:")
    for i, cpu in enumerate(cpu_info, start=1):
        print(f"CPU {i}:")
        for key, value in cpu.items():
            print(f"  - {key}: {value}")
    
    # Get RAM information
    ram_info_list = get_ram_info()
    print("RAM Information:")
    for i, ram_info in enumerate(ram_info_list, start=1):
        print(f"RAM Module {i}:")
        for key, value in ram_info.items():
            print(f"  - {key}: {value}")
    
    # Get GPU information
    gpu_info_list = get_gpus_info()
    print("GPU Information:")
    for i, gpu_info in enumerate(gpu_info_list, start=1):
        print(f"GPU {i}:")
        for key, value in gpu_info.items():
            print(f"  - {key}: {value}")
            
    # Get disk information
    disk_info_list = get_disk_info()
    print("Disk Infomation :")
    for i, disk_info in enumerate(disk_info_list, start=1):
        print(f"Disk {i}:")
        for key, value in disk_info.items():
            print(f"  - {key}: {value}")
            
    # Get network information
    network_info_list = get_network_info()
    print("Network Information:")
    for i, network_info in enumerate(network_info_list, start=1):
        print(f"Network Adapter {i}:")
        for key, value in network_info.items():
            print(f"  - {key}: {value}")
            
    print("-"*50)
    print("Host information retrieval completed.")
    print("-"*50)
    
    JSON_LOG['HOST-SPECS'] = {
        "CPU": cpu_info,
        "RAM": ram_info_list,
        "GPU": gpu_info_list,
        "Disk": disk_info_list,
        "Network": network_info_list
    }
    
    write_json(JSON_LOG, PATH_TO_JSON_LOG)
  
async def main():
 
    parser = argparse.ArgumentParser(description='Login and scrape data using Pyppeteer.')
 
    parser.add_argument('--username', required=False, help='The username for login')
 
    parser.add_argument('--password', required=False, help='The password for login')
    
    parser.add_argument('--dangerously-say-yes', action='store_true', help='Skip confirmation prompts')
    
    parser.add_argument('--skip-checked', action='store_true', help='Skip checked applications')
    
    parser.add_argument('--skip-host-check', action='store_true', help='Skip host information retrieval')
    
    parser.add_argument('--skip-installed',
                        action='store_true',
                        help='Skip checking installed applications')
    
    parser.add_argument('--async', action='store_true', help='Run application checks asynchronously')
    
    args = parser.parse_args()

    
    if args.dangerously_say_yes:
        print(Fore.RED + Back.YELLOW + ">>> Dangerously say yes is enabled. Skipping confirmation prompts.")
    
    # Runt the host info function
    if not SKIP_HOST_CHECK:
        await get_host_info()
 
    # Run the scraping function with command-line arguments
    await _scrape(**vars(args))
 

if __name__ == '__main__':
    asyncio.run(main())
   
 