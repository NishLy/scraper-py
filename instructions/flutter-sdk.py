from scrape.runner.powershell import run_powershell_with_text_output
from scrape.text import extract_words_by_pattern,VERSION_PATTERN
from scrape.instruction import Response,compare_app_version
from scrape.utils import download_and_save_file,extract_file,add_to_windows_path,remove_from_windows_path

RESOURCE_SOURCE_URL = "https://flutter.dev/docs/get-started/install/windows"
DOWNLOAD_SAVE_PATH = "D:\\src\\flutter.zip"
SYSTEM_PATH = "D:\\src\\flutter\\bin"
INSTALL_PATH = "D:\\src\\"
INSTALLED_SYSTEM_PATH = "D:\\src\\flutter\\bin"
INSTALLED_PATH = "D:\\src\\flutter"

COMMAND = r"flutter --version"

def main(requirements: dict[str, str]):
    for i in range(0,1):
        output = run_powershell_with_text_output(COMMAND)
        
        if output['stderr']:
            print("An error occurred:", output['stderr'], "Assuming Flutter is not installed. And trying to download it.")
            is_success = download_and_save_file(RESOURCE_SOURCE_URL, DOWNLOAD_SAVE_PATH)
            if is_success:
                print("File downloaded successfully. Try to extract it.")
                if extract_file(DOWNLOAD_SAVE_PATH,INSTALL_PATH):
                    print("File extracted successfully.")
                    if add_to_windows_path(SYSTEM_PATH):
                        print("Path added to system path. Try to run the command once again.")
                        continue
                    else:
                        return Response(False, "Failed to add path to system path.")
    
                return Response(False, "Failed to extract file.")
            return Response(False, "Failed to get Flutter, Decided to mark it as not installed. Please install Flutter manually.")
            
        result = extract_words_by_pattern(output["stdout"], VERSION_PATTERN)
        
        if not result:
            return Response(False, "Failed to extract version")
        
        if compare_app_version(result[0], requirements, "Flutter")["status"]:
            print("Flutter version is correct")
            return Response(True, "Flutter version is correct")
        
        print("Flutter version is not correct, Trying to remove the old version and install the new one.")
        print("Removing the old version of Flutter SYSTEM_PATH")
        if remove_from_windows_path(INSTALLED_SYSTEM_PATH):
            print("Old version removed successfully.")
            print("Trying repeat the installation process.")
            continue            
            
    return Response(False, "Failed to process Flutter installation")

    
# To debug locally, run the following in the terminal:
if __name__ == "__main__":
    main({"target": None, "minimum": "1.0.0"})