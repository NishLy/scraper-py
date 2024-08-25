from scrape.runner.powershell import run_powershell_with_text_output
from scrape.text import extract_words_by_pattern,VSC_EXTENSION_PATTERN
from scrape.instruction import Response,compare_app_version
from scrape.utils import download_and_save_file,extract_file,add_to_windows_path,remove_from_windows_path
from scrape.command import VSC_SHOW_EXTENSIONS_COMMAND,VSC_INSTALL_EXTENSION_COMMAND

VSC_EXTENSION_TO_INSTALL = ["code.dart","code.flutter"]

def main(requirements: dict[str, str]):
    for i in range(0,1):
        output = run_powershell_with_text_output(VSC_SHOW_EXTENSIONS_COMMAND)
        
        if output['stderr']:
            print("An error occurred:", output['stderr'], "Assuming Flutter is not installed. And trying to download it.")
        
            
        result = extract_words_by_pattern(output["stdout"], VSC_EXTENSION_PATTERN)
        
        if not result:
            return Response(False, "Failed to extract version")

        list_of_installed_extensions = []
        
        for i in range(0, len(result), 2):
            extension = result[i]
            version = result[i + 1]
            
            if extension not in VSC_EXTENSION_TO_INSTALL:
                continue    
            
            if compare_app_version(version, requirements, f"{extension}")["status"]:
                print(f'{extension} version is correct')
                list_of_installed_extensions.append(extension)
        
        if len(list_of_installed_extensions) == len(VSC_EXTENSION_TO_INSTALL):
            return Response(True, "All extensions are installed")

        print(list_of_installed_extensions)        
        print("Some extensions are not installed, Trying to install the missing ones.")
        
        for extension in VSC_EXTENSION_TO_INSTALL:
            if extension not in list_of_installed_extensions:
                print(f"Trying to install {extension}")
                command = f"{VSC_INSTALL_EXTENSION_COMMAND} {extension}"
                output = run_powershell_with_text_output(command)
                if output['stderr']:
                    print("An error occurred:", output['stderr'], f"Assuming {extension} is not installed. Trying to install it once again.")
                    continue
                
                print(f"Extension {extension} is installed")
   
            
    return Response(False, "Partial or no extensions are installed")


if __name__ == "__main__":
    print(main({"target": None, "minimum": "1.0.0"}))