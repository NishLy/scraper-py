import urllib.request
import sys
import os
import zipfile
import gzip
import tarfile
from pyunpack import Archive
import shutil


def download_and_save_file(url, destination)->bool:
    try:
        # Send a GET request to the URL and open the response
        with urllib.request.urlopen(url) as response:
            # Get the total file size (from Content-Length header)
            total_size = int(response.headers.get('Content-Length', 0))
            
            # Open the destination file to write the content
            with open(destination, 'wb') as file:
                downloaded_size = 0
                chunk_size = 8192  # 8KB chunks
                bar_length = 50     # Length of the progress bar
                
                # Download the file in chunks
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    
                    print_progress_bar(downloaded_size, total_size)
                
                sys.stdout.write("\nDownload complete!\n")
                return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    

def print_progress_bar(completed, total, bar_length=50):
    """
    Print a progress bar to the console.
    
    :param completed: Number of items completed
    :param total: Total number of items
    :param bar_length: Length of the progress bar
    """
    progress = (completed / total)
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f"\r[{bar}] {progress * 100:.2f}% Complete")
    sys.stdout.flush()

def extract_file(file_path, extract_to)->bool:
    """
    Extracts .7z, .gz, .zip, .tar, or .rar files to a specified directory with a progress bar.
    
    :param file_path: Path to the compressed file
    :param extract_to: Directory where files will be extracted
    :return: True if extraction was successful, False otherwise
    """
    # Ensure the destination directory exists
    os.makedirs(extract_to, exist_ok=True)
    
    # Determine the file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                total_files = len(zip_ref.infolist())
                for i, file_info in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file_info, extract_to)
                    print_progress_bar(i + 1, total_files)
                print("\nExtraction complete!")
        
        elif file_ext == '.rar':
            # pyunpack does not provide progress updates, so just handle extraction
            Archive(file_path).extractall(extract_to)
            print(f"\nExtracted '{file_path}' to '{extract_to}'")
        
        elif file_ext == '.7z':
            # pyunpack does not provide progress updates, so just handle extraction
            Archive(file_path).extractall(extract_to)
            print(f"\nExtracted '{file_path}' to '{extract_to}'")
        
        elif file_ext == '.tar':
            with tarfile.open(file_path, 'r') as tar_ref:
                total_files = len(tar_ref.getnames())
                for i, member in enumerate(tar_ref.getmembers()):
                    tar_ref.extract(member, extract_to)
                    print_progress_bar(i + 1, total_files)
                print("\nExtraction complete!")
        
        elif file_ext == '.gz':
            # Handle .gz files; they are often used with .tar files (e.g., .tar.gz)
            if file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
                with tarfile.open(file_path, 'r:gz') as tar_ref:
                    total_files = len(tar_ref.getnames())
                    for i, member in enumerate(tar_ref.getmembers()):
                        tar_ref.extract(member, extract_to)
                        print_progress_bar(i + 1, total_files)
                    print("\nExtraction complete!")
            else:
                # Single .gz file
                filename = os.path.join(extract_to, os.path.basename(file_path).replace('.gz', ''))
                with gzip.open(file_path, 'rb') as gz_ref:
                    with open(filename, 'wb') as out_file:
                        shutil.copyfileobj(gz_ref, out_file)
                print(f"\nExtracted '{file_path}' to '{filename}'")
        
        else:
            print("Unsupported file type.")
            return False
        
        return True
    except Exception as e:
        print(f"An error occurred while extracting the file: {e}")
        return False
    
    
def add_to_windows_path(directory)->bool:
    """
    Add a directory to the system PATH on Windows permanently.
    
    :param directory: Directory to add to PATH
    """
    try:
        import winreg
        
        # Get the current PATH value from the registry
        registry_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            current_path = winreg.QueryValueEx(key, 'Path')[0]
            if directory not in current_path:
                new_path = current_path + ';' + directory
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"Added '{directory}' to the system PATH.")
                return True
            else:
                print(f"'{directory}' is already in the system PATH. Treatment not necessary.")
                return True
    except Exception as e:
        print(f"An error occurred while updating the PATH: {e}")
        return False
    
import winreg

def remove_from_windows_path(directory)->bool:
    """
    Remove a directory from the system PATH on Windows.

    :param directory: Directory to remove from PATH
    """
    try:
        registry_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            # Get the current PATH value from the registry
            current_path = winreg.QueryValueEx(key, 'Path')[0]
            
            # Split the PATH into components
            paths = current_path.split(';')
            
            # Remove the directory if it exists
            new_paths = [path for path in paths if path.lower() != directory.lower()]
            new_path = ';'.join(new_paths)
            
            # Set the new PATH value
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"Removed '{directory}' from the system PATH.")
            return True
    except Exception as e:
        print(f"An error occurred while updating the PATH: {e}")
        return False