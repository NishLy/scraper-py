import asyncio.runners
import importlib
import subprocess
import sys
import os
import time
import platform
import threading
import argparse
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from functools import partial
from scrape.json import read_json, write_json
from scrape.module import check_required_modules

def _intro_ascii_art():
    print(Fore.CYAN + Style.BRIGHT + """

██╗   ██╗██████╗ ████████╗     █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ██████╗ ██╗   ██╗    ███╗   ██╗██╗███████╗██╗  ██╗
██║   ██║██╔══██╗╚══██╔══╝    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ██╔══██╗╚██╗ ██╔╝    ████╗  ██║██║██╔════╝██║  ██║
██║   ██║██████╔╝   ██║       ███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   ██║██║   ██║██╔██╗ ██║    ██████╔╝ ╚████╔╝     ██╔██╗ ██║██║███████╗███████║
██║   ██║██╔═══╝    ██║       ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ██╔══██╗  ╚██╔╝      ██║╚██╗██║██║╚════██║██╔══██║
╚██████╔╝██║        ██║       ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ██████╔╝   ██║       ██║ ╚████║██║███████║██║  ██║
 ╚═════╝ ╚═╝        ╚═╝       ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝    ╚═╝       ╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝
                                                                                                                                                                          
""")

#######################################################################################################################
# ENV SET / IF FAIL USE POWERSHEL TEMP ENV CHANGE
#######################################################################################################################

PYPPETEER_CHROMIUM_REVISION = '1263111' # Chromium revision used by pyppeteer
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

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
# CONSTANT VARS
INVENT_URL_FORM = 'http://127.0.0.1:5500/index.html'
INVENT_URL_LOGIN = 'http://127.0.0.1:5500/login.html'
CEKSOFT_URL_LOGIN = 'http://127.0.0.1:5500/ceksoft/login.php'
CEKSOFT_URL_FORM = 'http://127.0.0.1:5500/ceksoft'
PATH_TO_JSON_LOG =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'log.json')
PATH_INSTRUCTIONS = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'instructions')
KEYBOARD_MOUSE_TEST_SITE = 'https://en.kFey-test.ru/'
REQUIRED_MODULES = ['setuptools','pyppeteer','wmi','pytz','ntplib','platform','psutil','GPUtil','pyperclip','colorama','tabulate','pyunpack', 'patool','pywinauto']
#######################################################################################################################

#######################################################################################################################
# Loaded variable
#######################################################################################################################

_json_log = read_json(PATH_TO_JSON_LOG) if os.path.exists(PATH_TO_JSON_LOG) else {
    "Description": "This is a log file for the host information and the application status.",
    "HOST":{
        "PC-NAME": os.environ['COMPUTERNAME'],
        "OS": platform.system(),
        "OS-VERSION": platform.version(),
        "OS-RELEASE": platform.release(),
        "OS-ARCHITECTURE": platform.architecture(),
    },
    "HOST-SPECS":{},
    "APPLICATION-STATUS": {},
    "ARGS": {}
}

# Loaded available instructions
_instructions = []
if os.path.exists(PATH_INSTRUCTIONS):
    for file in os.listdir(PATH_INSTRUCTIONS):
        base, ext = os.path.splitext(file)
        if ext.lower() == '.py':
            _instructions.append(base.lower())
else:
    # close the app
    
    print(f"Instructions folder not found at {PATH_INSTRUCTIONS}. Please create a folder named 'instructions' in the same directory as this script.")
    sys.exit(1)

# Cheking required modules
check_required_modules(REQUIRED_MODULES)

#######################################################################################################################
#Late module import
#######################################################################################################################
from colorama import Fore, Style, init, Back
from scrape.instruction import compare_app_version
from scrape.time import set_time
from scrape.apps import find_installed_apps_by_registry,find_executable_on_path,find_installed_apps_by_getpackage
from scrape.host.check import check_virtualization,check_keyboard,check_mouse

init(autoreset=True)
 
def _show_prompt_confirmation(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")
 
 
def open_application(executable_path,app_name):
    print(Fore.CYAN + f"Opening {app_name} at {executable_path}")
    
    if not os.path.exists(executable_path):
        print(Fore.RED + f"Executable file not found at {executable_path}")
        return None
        
    result = find_executable_on_path(executable_path,app_name)
    
    if not result: 
        print(Fore.RED + f"No executable (MSI,EXE) files found for {app_name}. at {executable_path}")
        print(Back.MAGENTA + Fore.WHITE + "Please confirm the lines below (Cannot skiped in --dangerously-say-yes)")
        
        if _show_prompt_confirmation("Open the installation path? (y,n)"):
            subprocess.run(
            ['powershell', '-NoProfile', '-Command',f'explorer "{executable_path}"'], shell=True,check=True
        )

        _show_prompt_confirmation("Is in the installation path have executable file and it run successfuly ? (y,n)")
        return None

    if len(result) > 1:
        print(Fore.MAGENTA + f"Multiple executable found path '{app_name}'. Please select one" )
        
        dict = {}
        
        for path in result:
            dict[path] = path
        key = chose_app_to_open(dict)
        
        return subprocess.Popen([dict[key]])
    
    return subprocess.Popen([result[0]])
        
 
#######################################################################################################################
# Gui Functions
#######################################################################################################################

from scrape.host import get_current_network_config,set_network_config,get_network_interfaces
 
def show_network_popup():
    # Get available interfaces
    interfaces = get_network_interfaces()
    
    if not interfaces:
        messagebox.showerror("Error", "Failed to get network interfaces.")
        return 
    
      # GUI setup
    root = tk.Tk()
    root.title("Network Configuration")

    tk.Label(root, text="Select Interface:").grid(row=0, column=0, padx=10, pady=5)

    # Create radio buttons for each interface
    var_interface = tk.StringVar(value=interfaces[0] if interfaces else "")
    for idx, iface in enumerate(interfaces):
        tk.Radiobutton(root, text=iface, variable=var_interface, value=iface).grid(row=idx + 1, column=0, sticky='w', padx=10)

    # Load current config for the default selected interface
    if interfaces:
        config = get_current_network_config(interfaces[0])
    else:
        config = get_current_network_config("")
        
    tk.Label(root, text="IP Address:").grid(row=len(interfaces) + 1, column=0, padx=10, pady=5)
    ip_entry = tk.Entry(root)
    ip_entry.insert(0, config["ip"])
    ip_entry.grid(row=len(interfaces) + 1, column=1, padx=10, pady=5)

    tk.Label(root, text="Subnet Mask:").grid(row=len(interfaces) + 2, column=0, padx=10, pady=5)
    subnet_entry = tk.Entry(root)
    subnet_entry.insert(0, config["subnet"])
    subnet_entry.grid(row=len(interfaces) + 2, column=1, padx=10, pady=5)

    tk.Label(root, text="Gateway:").grid(row=len(interfaces) + 3, column=0, padx=10, pady=5)
    gateway_entry = tk.Entry(root)
    gateway_entry.insert(0, config["gateway"])
    gateway_entry.grid(row=len(interfaces) + 3, column=1, padx=10, pady=5)

    tk.Label(root, text="DNS Server:").grid(row=len(interfaces) + 4, column=0, padx=10, pady=5)
    dns_entry = tk.Entry(root)
    dns_entry.insert(0, config["dns"])
    dns_entry.grid(row=len(interfaces) + 4, column=1, padx=10, pady=5)

    def submit():
        selected_interface = var_interface.get()
        ip = ip_entry.get()
        subnet = subnet_entry.get()
        gateway = gateway_entry.get()
        dns = dns_entry.get()

        if selected_interface:
            if not set_network_config(selected_interface, ip, subnet, gateway, dns):
                messagebox.showerror("Error", "Failed to set network configuration.")
                return root.destroy()
            messagebox.showinfo("Success", "Network configuration has been set successfully.")
            return root.destroy()
        else:
            messagebox.showerror("Error", "Please select a network interface.")

    submit_button = tk.Button(root, text="Apply", command=submit)
    submit_button.grid(row=len(interfaces) + 5, column=0, columnspan=2, pady=10)
    
    cancel_button = tk.Button(root, text="Cancel", command=root.destroy)    
    cancel_button.grid(row=len(interfaces) + 5, column=1, pady=10)

    root.mainloop()
    
 
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
    messagebox.geometry("600x200")  # Increase width, reduce height
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
# CONSTANT CHECK Functions
#######################################################################################################################

def check_chrome():
    result = subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe"])
    print(result)
    return result

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
#CONSTANT VALUE / CHECK
#######################################################################################################################

CONSTANT_CHECK = {
    "date-time": {
        "function": partial(set_time,"Asia/Bangkok"),
       " message_success": "Date & Time has been set successfully.",
        "message_fail": "Date & Time has not been set.",
        "message_confirmation": "Do you want to set the Date & Time to UTC +7?"
    },
    "mouse": {
        "function": partial(check_mouse,KEYBOARD_MOUSE_TEST_SITE),
        "message_success": "Mouse is working.",
        "message_fail": "Mouse is not working.",
        "message_confirmation": "Is the mouse working properly?"
    },
    "keyboard": {
        "function": partial(check_keyboard,KEYBOARD_MOUSE_TEST_SITE),
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
    },
    "python": {
        "function": lambda: subprocess.Popen(["python", "--version"]),
        "message_success": "Python is installed.",
        "message_fail": "Python is not installed.",
        "message_confirmation": "Is Python installed?"
    },
}

#######################################################################################################################
# Application Check Functions
#######################################################################################################################

def _handle_requirement(app_name,requirement,curent_version):
    try:
        if not requirement:
            return True
        
        print("Requirement are declared, Try to match {app_name} requirement")
        
        if requirement['target'] != None and requirement['target'] == curent_version:
            print("Requirement target does not match do you want to unistall it?")
            _show_prompt_confirmation("Please enter (y/n) : ")
        
        if requirement['target'] == None and requirement['minimum'] <= curent_version:
            print("Requirement minimum are fullfiled, and continue checking sequence")
            return True
            
    finally :
        print("Something error in requirement type. deciding to continue checking without requirement")  
        return False


def chose_app_to_open(app_list):
    for i,app in enumerate(app_list):
        print(f"{i}. {app}")
        
    is_in_invalid = True
    
    while is_in_invalid:
        input_num = input(Fore.WHITE + Back.MAGENTA + f"Input number to chose or 'all' to open each instalation path : ")
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

import pythoncom

def _check_app(label_app_name,**kwargs):
    pythoncom.CoInitialize()
    print(f"Running function check_app on thread: {threading.current_thread().name}")
    
    if label_app_name in _json_log['APPLICATION-STATUS']:
        del _json_log['APPLICATION-STATUS'][label_app_name]

    log_app = {
        "Name": label_app_name,
        "Status" : "NOT_INSTALLED", # NOT_INSTALLED, INSTALLED
        "Install_Location": "N/A",
        "Version" : "N/A",
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
        
    if not check_with and (result := find_installed_apps_by_getpackage(label_app_name.replace("-", ""))) not in [None, {}]:
        print(Fore.CYAN + f"{label_app_name} is detected GET-PACKAGE | WHERE-OBJECT. Trying to open the application...")
        if all(result[app]['source'] == "N/A" for app in result):
            print(Fore.BLACK + Back.YELLOW + f"{label_app_name} found GET-PACKAGE | WHERE-OBJECT, But GET-PACKAGE | WHERE-OBJECT cannot provide instalation path. Skiping  GET-PACKAGE | WHERE-OBJECT or try open it manualy")
            log_app["Description"] = log_app["Description"] + " - " + f"{label_app_name} found GET-PACKAGE | WHERE-OBJECT, But GET-PACKAGE | WHERE-OBJECT cannot provide instalation path."
        else:
            try:
                key = 0
                if len(result) > 1:
                    print(Fore.MAGENTA + f"Multiple installations found GET-PACKAGE | WHERE-OBJECT for '{label_app_name}'. Please select or open each istalation path" )
                    key = chose_app_to_open(result)
                else:
                    key = list(result.keys())[0]
                
                evaluate = None
                
                if key != -1:
                    evaluate = open_application(result[key],label_app_name)
                
                if show_confirmation_popup(f"Did {label_app_name} working successfully?\n { f"Current version of {compare_app_version(result[key]['version'],kwargs.get("requirement"),label_app_name)['message']}" if kwargs.get('requirement',False) else "This app doesnt specify version"}",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Install_Location"] = result[key]['source']
                    log_app["Description"] = f'{label_app_name} is working.'
                else:
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] = f'{label_app_name} is not working.'
                if evaluate and type(evaluate) == subprocess.Popen:
                    evaluate.terminate()
                check_with = "GETPACKAGE | WHERE-OBJECT"
                log_app['Version'] = result[key]['version']
                
            except Exception as e:
                print(Back.RED + Fore.WHITE + f"Error open {label_app_name} with  GET-PACKAGE | WHERE-OBJEC : {str(e)}")
                print(Back.YELLOW + Fore.BLACK + "Skiping 'GET-PACKAGE | WHERE-OBJECT' because error occured")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] = log_app["Description"] + " - " + f"Error loading module: {str(e)}"    
                            
    if not check_with and (result := find_installed_apps_by_registry(label_app_name.replace("-", ""))) not in [None, {}] :
        print(Fore.CYAN + f"{label_app_name} is detected in REGISTRY. Trying to open the application...")
        if all(result[app]['source'] == "N/A" for app in result):
            print(Fore.BLACK + Back.YELLOW + f"{label_app_name} found in REGISTRY, But REGISTRY cannot provide instalation path. Skiping REGISTRY or try open it manualy")
            log_app["Description"] = log_app["Description"] + " - " + f"{label_app_name} found in REGISTRY, But REGISTRY cannot provide instalation path."
        else:
            try:
                key = 0
                if len(result) > 1:
                    print(Fore.MAGENTA + f"Multiple installations in REGISTRY found for '{label_app_name}'. Please select or open each istalation path" )
                    result_modified = {app:result[app]['source'] for app in result}
                    key = chose_app_to_open(result_modified)
                else:
                    key = list(result.keys())[0]
                
                evaluate = None
                
                if key != -1:
                    evaluate = open_application(result[key]['source'],label_app_name)
                    
                if show_confirmation_popup(f"Did '{label_app_name}' working successfully?\n { f"Current version of {compare_app_version(result[key]['version'],kwargs.get("requirement"),label_app_name)['message']}" if kwargs.get('requirement',False) else "This app doesnt specify version"}",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Install_Location"] = result[key]['source']
                    log_app["Description"] = f'{label_app_name} is working.'
                else:
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] = f'{label_app_name} is not working.'
                    
                if evaluate and type(evaluate) == subprocess.Popen:
                    evaluate.terminate()
                check_with = "REGISTRY"
                log_app['Version'] = result[key]['version']
                
            except Exception as e:
                print(Back.RED + Fore.WHITE + f"Error open {label_app_name} with REGISTRY : " + str(e))
                print(Back.YELLOW + Fore.BLACK + "Skiping 'REGISTRY' because error occured")
                log_app["Status"] = "NOT_INSTALLED"
                log_app["Description"] = f"Error opening {label_app_name} : " + str(e)

    if not check_with and label_app_name.lower() in _instructions:
        print(Fore.CYAN + f"{label_app_name} is available in instructions. Trying to run the function...")
        try:
            # Get the module name (without .py extension)
            module_name = label_app_name.lower()

            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, PATH_INSTRUCTIONS + "/" + label_app_name.lower() + '.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'main'):
                requirement = kwargs.get("requirement") if kwargs.get("requirement") else {"target":None,"minimum":None}
                
                evaluate = module.main(requirement)
        
                if not kwargs.get("no_confirm",False):
                    if evaluate['status']:
                        print(Fore.YELLOW + f"{label_app_name} is working?. Instruction result -> {evaluate['message']}")
                    else:
                        print(Fore.YELLOW + f"{label_app_name} is not working?. Instruction result -> {evaluate['message']}")
                        
                if show_confirmation_popup(f"Instruction has been executed, Did {label_app_name} work successfully?",no_confirm=kwargs.get("dangerously_say_yes",False),evaluate=evaluate['status']):
                    print(Fore.GREEN + f">>> {label_app_name} is working. Marked as installed.")
                    log_app["Status"] = "INSTALLED"
                    log_app["Description"] = f"{evaluate['message']}"
                else:       
                    print(Fore.RED + f">>> {label_app_name} is not working. Marked as not installed.")
                    log_app["Status"] = "NOT_INSTALLED"
                    log_app["Description"] =  f"{evaluate['message']}"
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
    _json_log['APPLICATION-STATUS'][label_app_name] = log_app
    write_json(_json_log, PATH_TO_JSON_LOG)
    pythoncom.CoUninitialize()
    

async def _check_applications(apps, **kwargs):
    print("Main thread :", threading.current_thread().name)
    
    async def run_in_thread(label_app_name,**kwargs):
        from functools import partial
        loop = asyncio.get_running_loop()
        partial_func = partial(_check_app,label_app_name,**kwargs)
        result = await loop.run_in_executor(None,partial_func)
        return result
    
    print('-' * 100)
    print("Start checking each required app or tools.")
    print('-' * 100)

    tasks = []
    checked_apps = [app for app in _json_log['APPLICATION-STATUS']]
    installed_apps = None
    
    if kwargs.get('skip_installed',False):
        installed_apps = [app for app in _json_log['APPLICATION-STATUS'] if _json_log['APPLICATION-STATUS'][app]['Status'] == 'INSTALLED']
    
    for label_app_name,requirement in zip(apps,kwargs.get('requirements')):
        kwargs['requirement'] = requirement
        label_app_name = label_app_name.lower()
        
        if kwargs.get('skip_checked',False) and label_app_name in checked_apps:
            print(f"{label_app_name} has been checked before. Skipping...")
            continue
        if installed_apps and label_app_name in installed_apps:
            print(f"{label_app_name} has been marked installed before. Skipping...")
            continue
        
        if kwargs.get('async',False):
            tasks.append(run_in_thread(label_app_name,**kwargs))
        else:
            _check_app(label_app_name,**kwargs)
            

    if kwargs.get('async',False):
        results = await asyncio.gather(*tasks)
            
    print('-' * 100)
    print("Cheking apps completed.")
    print('-' * 100)
        
 #######################################################################################################################
# FUNTIONS TO GET HOST INFO
#######################################################################################################################

from scrape.host import get_cpu_info,get_gpus_info,get_network_info,get_disk_info,get_ram_info,get_motherboard_info

async def get_host_info():

    # Get CPU information
    cpu_info = get_cpu_info()

    # Get RAM information
    ram_info_list = get_ram_info()
    
    # Get GPU information
    gpu_info_list = get_gpus_info()
            
    # Get disk information
    disk_info_list = get_disk_info()
            
    # Get network information
    network_info_list = get_network_info()
    
    # Get motherboard information
    motherboard_info = get_motherboard_info()
    
    _json_log['HOST-SPECS'] = {
        "CPU": cpu_info,
        "RAM": ram_info_list,
        "GPU": gpu_info_list,
        "Disk": disk_info_list,
        "Network": network_info_list,
        "Motherboard": motherboard_info
    }
    
    write_json(_json_log, PATH_TO_JSON_LOG)

#######################################################################################################################
# Scraping Functions
#######################################################################################################################

import json
from pyppeteer import launch

async def _scrape_ceksoft(username, password, **kwargs):
 
    labels = None
    browser = await launch(headless=False,timeout=60000)
    try:
        # Launch a new browser instance
 
        page = await browser.newPage()
 
        # Navigate to the login page
 
        await page.goto(CEKSOFT_URL_LOGIN)  # Replace with your login page URL
 
        # Fill out the login form
 
        await page.type('[name="username"]', username)  # Replace with your username input selector
 
        await page.type('[name="password"]', password)  # Replace with your password input selector
 
        # Submit the login form
 
        await page.click('[name="login"]')  # Replace with your login button selector
 
        await page.waitForNavigation()    # Wait for navigation to complete
 
        labels = await page.evaluate('''
 
            () => {
 
                // Find the table with the specific ID
 
                const table = document.querySelector('#dataSoftware');
 
                if (!table) return [];
 
 
                // Get all rows in the table
 
                const rows = table.querySelectorAll('tr');
 
                const extractedTexts = [];
 
 
                rows.forEach(row => {
 
                    // Find the first cell in the row
 
                    const firstCell = row.querySelector('td');
 
                    if (firstCell) {
 
                        // Find the label element within the first cell
 
                        const label = firstCell.querySelector('label');
 
                        if (label) {
 
                            extractedTexts.push(label.textContent.trim());
 
                        }
 
                    }
 
                });
 
 
                return extractedTexts;
 
            }
 
        ''')
        
        return labels
    except Exception as e:
        print("ERror on scarping ceksoft : " + str(e))
    finally:
        await browser.close()
    return labels
       
 

 
async def _send_report_invent(invent:dict,**kwargs):
    browser = await launch(headless=False,timeout=60000)
    try:
        page = await browser.newPage()

        await page.goto(INVENT_URL_FORM)
        
        await page.waitForSelector('.form-horizontal')
        
        await page.evaluate('document.querySelector(".form-horizontal").reset()')
        
        await page.type('[name="nm_brg"]', invent['HOST']['PC-NAME'])  
        
        await page.type('[name="jumlah"]', '1')  
        
        await page.type('[name="posisi"]', kwargs.get("pc_position") if kwargs.get("pc_position") else "N/A")
        
        await page.type('[name="processor"]', invent['HOST-SPECS']['CPU'][0]['Name'])  
        
        await page.type('[name="motherboard"]', invent['HOST-SPECS']['Motherboard'][0]['Manufacturer'] + " " + invent['HOST-SPECS']['Motherboard'][0]['Model'])
        
        await page.type('[name="hdd"]', invent['HOST-SPECS']['Disk'][0]['Model'] + " " + invent['HOST-SPECS']['Disk'][0]['Size (GB)'])
        
        await page.type('[name="ram1"]', invent['HOST-SPECS']['RAM'][0]['Type'] + " " + invent['HOST-SPECS']['RAM'][0]['Size (GB)']) 
        
        await page.type('[name="ram1"]', invent['HOST-SPECS']['RAM'][1]['Type'] + " " + invent['HOST-SPECS']['RAM'][1]['Size (GB)'] if len(invent['HOST-SPECS']['RAM']) > 1 else "N/A")

        await page.type('[name="vga"]', invent['HOST-SPECS']['GPU'][0]['Name'] + " " + str(invent['HOST-SPECS']['GPU'][0]['VRAM (GB)']))
        
        await page.type('[name="cardlan"]', invent['HOST-SPECS']['Network'][0]['Description'] + " " + invent['HOST-SPECS']['Network'][0]['MACAddress'])    
        
        await page.type('[name="tanggal_inven"]', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        
    finally:
        await browser.close()

#######################################################################################################################
# Main Function
#######################################################################################################################

  
async def main():
    _intro_ascii_art()
    
    # Parsing arguments
    parser = argparse.ArgumentParser(description='Login and scrape data using Pyppeteer.')
    parser.add_argument('--username', required=False, help='The username for login')
    parser.add_argument('--password', required=False, help='The password for login')
    parser.add_argument('--dangerously-say-yes', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--skip-checked', action='store_true', help='Skip checked applications')
    parser.add_argument('--skip-host-check', action='store_true', help='Skip host information retrieval')
    parser.add_argument('--skip-installed', action='store_true', help='Skip checking installed applications')
    parser.add_argument('--async', action='store_true', help='Run application checks asynchronously')
    parser.add_argument('--no-report', action='store_true', help='Skip sending the report')
    parser.add_argument('--pc-position', required=False, help='The position of the device')
    parser.add_argument('--pc-number', required=False, help='The number of the device')
    parser.add_argument('--set-network', action='store_true', help='Set network configuration')
    parser.add_argument('--custom-data', required=False, help='Custom data to replace the default data')
    args = parser.parse_args()
    
    if args.set_network:
        show_network_popup()

    _json_log['ARGS'] = vars(args)

    if args.dangerously_say_yes:
        print(Fore.RED + Back.YELLOW + ">>> Dangerously say yes is enabled. Skipping confirmation prompts.")
        
    # do query
    if args.custom_data:
        os.path.exists(args.custom_data)
        with open(args.custom_data) as f:
            txt = f.read()
            labels = txt.split("\n")
    else:
        labels =  await _scrape_ceksoft(args.username,args.password)
    
    if not labels:
        print("Error Fetching Labels : " + labels)
        return sys.exit(1)
    
    # Print the extracted text
    # labels = ['git','date-time','winrar','flutter-sdk={"target":null,"minimum":"1.19.2"}',"visual-studio-code",'flutter-extension','virtualization','git', 'virtual-box', 'chrome']
    requirements = [ label.split('=')[1] if len(label.split("=")) == 2 else None for label in labels ]
    labels = [ label.split("=")[0] for label in labels ]
    
    def add_name(x,i):
        try:
            loaded = json.loads(x)
            loaded['name'] = labels[i]
            return loaded
        except:
            return None
    
    requirements = [add_name(requirement,i) if requirement else None for i,requirement in enumerate(requirements)]
    
    kwargs = vars(args)
    kwargs['requirements'] = requirements
    # Running host info function
    if not args.skip_host_check:
        await get_host_info()
    
    # Print applications to check
    
    print('-' * 100)
    print("Applications to check:")
    print('-' * 100)
    
    for label in labels:
        print(f"- {label}")
    
    # Check applications
    await _check_applications(labels, **kwargs)
    
    print('-' * 100)
    print("Checking applications completed.")
    print('-' * 100)
    
    # Print host information
    print("-" * 100)
    print("Host Information")
    print("-" * 100)

    for segment in _json_log['HOST-SPECS']:
        print(f"{segment} Information\n")
        for i, device in enumerate(_json_log['HOST-SPECS'][segment]):
            print(f" {segment} {i}")
            for key in device:
                print(f" {key} : {device[key]}")
            print()
        print("-" * 100)

    # Print application status
    print("-" * 100)
    print("Apps Status")
    print("-" * 100)

    for i, app in enumerate(_json_log['APPLICATION-STATUS']):
        print(f"App {i}")
        print(f"Name : {app}")
        print(f"Status : {_json_log['APPLICATION-STATUS'][app]['Status']}")
        print(f"Install Location : {_json_log['APPLICATION-STATUS'][app]['Install_Location']}")
        print(f"Version : {_json_log['APPLICATION-STATUS'][app]['Version']}")
        print(f"Description : {_json_log['APPLICATION-STATUS'][app]['Description']}")
        print(f"Check Duration : {_json_log['APPLICATION-STATUS'][app]['Check_Time']} seconds")
        print(f"Check with : {_json_log['APPLICATION-STATUS'][app]['Check_with']}")
        print("-" * 100)

    try:
        # Sending the report if required
        if not args.no_report:
            await _send_report_invent(_json_log, **vars(args))
    except Exception as e:
        print(f"Error sending the report: {e}")
 
if __name__ == '__main__':
    asyncio.run(main())
   
   
   
 