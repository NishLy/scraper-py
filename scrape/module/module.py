#######################################################################################################################
# Check module function
#######################################################################################################################
import importlib
import subprocess
import sys

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
        
def check_required_modules(_required_modules, _install_missing=True):
    for module_name in _required_modules:
        if not check_module_installed(module_name):
            print(f"Module '{module_name}' is not installed. Installing...")
            if _install_missing:
                install_module(module_name)
            else:
                print(f"Module '{module_name}' is required but not installed.")
                sys.exit(1)
    print("All required modules are installed.")
 